#ifndef COMMON_H
#define COMMON_H

#include <stdint.h>

#define TCP_PORT 5060
#define SYNC_TAG 0x55AA55AA

#define STATUS_INCL_OK    (1 << 0)
#define STATUS_ENCODER_OK (1 << 1)

#pragma pack(push, 1)
typedef struct {
    uint32_t sync;      // 0x55AA55AA
    uint16_t seq;       // Sequence number
    uint64_t timestamp; // Unix timestamp in ms
    double distance;    // Meters
    double tilt;        // Degrees
    float gauge;        // Constant
    uint8_t crc;        // Checksum
    uint8_t status;     // Hardware Health Status Bits
} sensor_packet_t;
#pragma pack(pop)

#endif // COMMON_H
