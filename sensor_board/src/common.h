#ifndef COMMON_H
#define COMMON_H

#include <stdint.h>

#define TCP_PORT 5060
#define SYNC_TAG 0xAA55

#pragma pack(push, 1)
typedef struct {
    uint16_t sync;      // 0xAA55
    uint16_t seq;       // Sequence number
    uint64_t timestamp; // Unix timestamp in ms
    double distance;    // Meters
    double tilt;        // Degrees
    float gauge;        // Constant 1676.0
    uint8_t crc;        // Simple checksum
} sensor_packet_t;
#pragma pack(pop)

#endif // COMMON_H
