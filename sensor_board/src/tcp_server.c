#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include "common.h"

extern void get_sensor_packet(sensor_packet_t *packet);
extern int init_hardware();

void *stream_thread(void *arg) {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(TCP_PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        perror("Listen failed");
        exit(EXIT_FAILURE);
    }

    printf("[TCP] Server listening on port %d...\n", TCP_PORT);

    while (1) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("Accept failed");
            continue;
        }
        printf("[TCP] Client connected\n");

        while (1) {
            sensor_packet_t packet;
            get_sensor_packet(&packet);
            
            if (send(new_socket, &packet, sizeof(packet), 0) <= 0) {
                printf("[TCP] Client disconnected\n");
                close(new_socket);
                break;
            }
            usleep(10000); // 100 Hz Streaming
        }
    }
    return NULL;
}

int main() {
    if (init_hardware() != 0) {
        printf("Hardware initialization failed. Running in simulation mode.\n");
    }

    pthread_t thread;
    pthread_create(&thread, NULL, stream_thread, NULL);
    pthread_join(thread, NULL);

    return 0;
}
