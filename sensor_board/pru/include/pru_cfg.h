#ifndef _PRU_CFG_H_
#define _PRU_CFG_H_

#include <stdint.h>

/* Minimal PRU_CFG register set for AM335x */
typedef struct {
	volatile uint32_t REVID;
	volatile uint32_t rsvd0[3];
	volatile uint32_t SYSCFG;
	volatile uint32_t rsvd1[15];
	volatile uint32_t GPCFG0;
	volatile uint32_t GPCFG1;
	volatile uint32_t rsvd2[2];
	volatile uint32_t CTPP_CFG;
} pruCfg;

#endif /* _PRU_CFG_H_ */
