#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <stdint.h>
#include <sys/mman.h>
#include <math.h>
#include <time.h>
#include "common.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define PRU_SHARED_RAM 0x4A310000 
#define PRU_RAM_SIZE 0x3000

static int spi_fd = -1;
static uint32_t *pru_mem = NULL;

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

double read_scl3300() {
    // SCL3300 Read Tilt (X-axis) - 32-bit Off-frame protocol
    // Command: 0x040000F7 -> [0x04, 0x00, 0x00, 0xF7]
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
    
    if (ioctl(spi_fd, SPI_IOC_MESSAGE(1), &tr) < 0) return 0.0;
    
    // Validate CRC of the frame received (rx[3] is CRC)
    uint8_t calc = calculate_crc8(rx, 3);
    if (calc != rx[3]) {
        // Log CRC error if needed
        return 0.0; 
    }

    // Convert 16-bit payload from frame (rx[1]=MSB, rx[2]=LSB)
    int16_t raw = (int16_t)((rx[1] << 8) | rx[2]);
    
    // Sensitivity for SCL3300 (Mode 1: 12000 LSB/g)
    // Degrees = arcsin(raw / 12000)
    double g = (double)raw / 12000.0;
    if (g > 1.0) g = 1.0;
    if (g < -1.0) g = -1.0;
    return asin(g) * (180.0 / M_PI);
}

int32_t read_encoder() {
    if (pru_mem) {
        return (int32_t)pru_mem[0]; // Offset 0 was count in our PRU code
    }
    return 0;
}

void get_sensor_packet(sensor_packet_t *packet) {
    static uint16_t seq = 0;
    packet->sync = SYNC_TAG;
    packet->seq = seq++;
    packet->timestamp = (uint64_t)time(NULL) * 1000;
    
    // Scale encoder: 4000 pulses/rev, 200mm/rev -> 0.05mm per pulse
    packet->distance = (double)read_encoder() * 0.00005; 
    
    packet->tilt = read_scl3300();
    packet->gauge = 1676.0f;
    packet->crc = calculate_packet_checksum(packet);
}
