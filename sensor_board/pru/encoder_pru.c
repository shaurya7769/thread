#include <stdint.h>
#include <pru_cfg.h>
#include <pru_ctrl.h>
#include "resource_table.h"

/* 
 * PRU Encoder Decoder
 * Inputs: 
 *   A -> P8.12 (PRU1_R31[14])
 *   B -> P8.11 (PRU1_R31[15])
 * 
 * Shared Memory Structure:
 * OFFSET 0: int32_t count
 * OFFSET 4: uint32_t status
 */

volatile register uint32_t __R30;
volatile register uint32_t __R31;

#define SHARED_MEM_BASE 0x10000 // PRU Shared RAM

void main(void) {
    uint32_t *shared_mem = (uint32_t *)SHARED_MEM_BASE;
    uint32_t last_state = 0;
    int32_t count = 0;

    /* Clear shared memory */
    shared_mem[0] = 0;
    shared_mem[1] = 1; // IDLE

    /* Quadrature lookup table */
    /* format: [new_A, new_B, old_A, old_B] */
    const int8_t lookup[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};

    while (1) {
        uint32_t current_pins = (__R31 >> 14) & 0x03; // Mask bits 14 and 15
        
        if (current_pins != last_state) {
            uint32_t index = (last_state << 2) | current_pins;
            count += lookup[index & 0x0F];
            
            shared_mem[0] = count;
            last_state = current_pins;
        }
    }
}
