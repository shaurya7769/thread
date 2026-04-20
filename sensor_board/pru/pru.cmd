/* Map PRU memory for AM335x */

MEMORY
{
    PAGE 0:
      PRU_IMEM     : org = 0x00000000 len = 0x00002000  /* 8kB PRU Instruction RAM */

    PAGE 1:
      PRU_DMEM_0_1 : org = 0x00000000 len = 0x00002000 CREGISTER=24 /* 8kB PRU Data RAM 0_1 */
      PRU_DMEM_1_0 : org = 0x00002000 len = 0x00002000 CREGISTER=25 /* 8kB PRU Data RAM 1_0 */
      PRU_SHAREDMEM: org = 0x00010000 len = 0x00003000 CREGISTER=28 /* 12kB Shared RAM */
}

SECTIONS
{
    .text           > PRU_IMEM, PAGE 0
    .stack          > PRU_DMEM_0_1, PAGE 1
    .bss            > PRU_DMEM_0_1, PAGE 1
    .cio            > PRU_DMEM_0_1, PAGE 1
    .const          > PRU_DMEM_0_1, PAGE 1
    .data           > PRU_DMEM_0_1, PAGE 1
    .switch         > PRU_DMEM_0_1, PAGE 1
    .sysmem         > PRU_DMEM_0_1, PAGE 1
    .cinit          > PRU_DMEM_0_1, PAGE 1
    .resource_table > PRU_DMEM_0_1, PAGE 1
}
