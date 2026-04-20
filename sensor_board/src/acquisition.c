#define _DEFAULT_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <stdint.h>
#include <sys/mman.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include "common.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define PRU_SHARED_RAM 0x4A310000 
#define PRU_RAM_SIZE 0x3000

#define AVG_WINDOW 20
#define POLL_INTERVAL_US 2000 // 500 Hz

static int spi_fd = -1;
static uint32_t *pru_mem = NULL;

// Circular Buffer for Averaging
static double tilt_buffer[AVG_WINDOW] = {0};
static int tilt_idx = 0;
static double tilt_sum = 0;
static pthread_mutex_t data_mutex = PTHREAD_MUTEX_INITIALIZER;
static int buffer_filled = 0;

// SCL3300 Hardware CRC-8 (Polynomial 0x1D)
uint8_t calculate_crc8(uint8_t *data, int len) {
    uint8_t crc = 0xFF; // Initialization
    for (int j = 0; j < len; j++) {
        crc ^= data[j];
        for (int i = 0; i < 8; i++) {
            if (crc & 0x80) crc = (uint8_t)((crc << 1) ^ 0x1D);
            else crc <<= 1;
        }
    }
    return (uint8_t)(crc ^ 0xFF); // Final XOR
}

// Packet Checksum (Simple XOR for TCP integrity)
uint8_t calculate_packet_checksum(sensor_packet_t *p) {
    uint8_t *data = (uint8_t *)p;
    uint8_t crc = 0;
    for (int i = 0; i < sizeof(sensor_packet_t) - 1; i++) {
        crc ^= data[i];
    }
    return crc;
}

int init_hardware() {
    // 1. SPI Setup
    spi_fd = open("/dev/spidev0.0", O_RDWR);
    if (spi_fd < 0) {
        perror("Failed to open SPI");
        return -1;
    }
    uint8_t mode = 0; // Mode 0
    uint32_t speed = 2000000; // 2 MHz
    ioctl(spi_fd, SPI_IOC_WR_MODE, &mode);
    ioctl(spi_fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed);

    // 2. PRU Memory Setup
    int mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem_fd < 0) {
        perror("Failed to open /dev/mem");
        return -1;
    }
    pru_mem = mmap(NULL, PRU_RAM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, mem_fd, PRU_SHARED_RAM);
    close(mem_fd);

    if (pru_mem == MAP_FAILED) {
        perror("mmap failed");
        return -1;
    }
    
    // Clear PRU memory to ensure encoder starts at 0
    pru_mem[0] = 0; 

    // 3. SCL3300 Initialization Sequence
    uint8_t wakeup[] = {0x1C, 0x00, 0x00, 0xAD}; // Wake up
    uint8_t mode1[]  = {0x14, 0x00, 0x00, 0xC7}; // Change to mode 1
    
    struct spi_ioc_transfer tr[1] = {0};
    tr[0].tx_buf = (unsigned long)wakeup;
    tr[0].len = 4;
    tr[0].speed_hz = 2000000;
    
    ioctl(spi_fd, SPI_IOC_MESSAGE(1), tr);
    usleep(100000); // 100ms
    
    tr[0].tx_buf = (unsigned long)mode1;
    ioctl(spi_fd, SPI_IOC_MESSAGE(1), tr);
    usleep(100000); // 100ms

    return 0;
}

double read_scl3300_raw() {
    static int crc_error_count = 0;
    
    // SCL3300 Read Tilt (X-axis) - 32-bit Off-frame protocol
    uint8_t tx[] = {0x04, 0x00, 0x00, 0xF7}; 
    uint8_t rx[4] = {0};
    struct spi_ioc_transfer tr = {
        .tx_buf = (unsigned long)tx,
        .rx_buf = (unsigned long)rx,
        .len = 4,
        .speed_hz = 2000000,
        .delay_usecs = 10,
        .bits_per_word = 8,
    };
    
    if (ioctl(spi_fd, SPI_IOC_MESSAGE(1), &tr) < 0) {
        crc_error_count++;
    } else {
        uint8_t calc = calculate_crc8(rx, 3);
        if (calc != rx[3]) {
            crc_error_count++;
        } else {
            crc_error_count = 0;
            int16_t raw = (int16_t)((rx[1] << 8) | rx[2]);
            double g = (double)raw / 12000.0;
            if (g > 1.0) g = 1.0;
            if (g < -1.0) g = -1.0;
            return asin(g) * (180.0 / M_PI);
        }
    }

    if (crc_error_count > 5) {
        uint8_t wakeup[] = {0x1C, 0x00, 0x00, 0xAD}; 
        uint8_t mode1[]  = {0x14, 0x00, 0x00, 0xC7};
        struct spi_ioc_transfer tr_init = { .tx_buf = (unsigned long)wakeup, .len = 4, .speed_hz = 2000000 };
        ioctl(spi_fd, SPI_IOC_MESSAGE(1), &tr_init);
        usleep(50000);
        tr_init.tx_buf = (unsigned long)mode1;
        ioctl(spi_fd, SPI_IOC_MESSAGE(1), &tr_init);
        usleep(50000);
        crc_error_count = 0;
    }
    return 0.0;
}

void *polling_thread(void *arg) {
    while (1) {
        double val = read_scl3300_raw();
        
        pthread_mutex_lock(&data_mutex);
        tilt_sum -= tilt_buffer[tilt_idx];
        tilt_buffer[tilt_idx] = val;
        tilt_sum += val;
        tilt_idx = (tilt_idx + 1) % AVG_WINDOW;
        if (!buffer_filled && tilt_idx == 0) buffer_filled = 1;
        pthread_mutex_unlock(&data_mutex);
        
        usleep(POLL_INTERVAL_US);
    }
    return NULL;
}

void start_polling() {
    pthread_t thread;
    pthread_create(&thread, NULL, polling_thread, NULL);
    pthread_detach(thread);
}

int32_t read_encoder() {
    if (pru_mem) {
        return (int32_t)pru_mem[0];
    }
    return 0;
}

void get_sensor_packet(sensor_packet_t *packet) {
    static uint16_t seq = 0;
    packet->sync = SYNC_TAG;
    packet->seq = seq++;
    
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    packet->timestamp = (uint64_t)ts.tv_sec * 1000 + (ts.tv_nsec / 1000000);
    
    // Scale encoder: 4000 pulses/rev, 200mm/rev -> 0.00005m per pulse
    packet->distance = (double)read_encoder() * 0.00005; 
    
    pthread_mutex_lock(&data_mutex);
    packet->tilt = tilt_sum / (buffer_filled ? AVG_WINDOW : (tilt_idx ? tilt_idx : 1));
    pthread_mutex_unlock(&data_mutex);
    
    packet->gauge = 1676.0f; // Constant as requested
    packet->crc = calculate_packet_checksum(packet);
}
