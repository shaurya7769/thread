#ifndef _RSC_TABLE_PRU_H_
#define _RSC_TABLE_PRU_H_

#include <stddef.h>
#include <rsc_types.h>
#include "pru_virtio_ids.h"

struct my_resource_table {
    struct resource_table base;
    uint32_t offset[1];
};

#if !defined(__GNUC__)
#pragma DATA_SECTION(resourceTable, ".resource_table")
#pragma RETAIN(resourceTable)
#endif

#ifdef __GNUC__
__attribute__((section(".resource_table")))
#endif

struct my_resource_table resourceTable = {
    1,      /* Resource table version */
    0,      /* Number of resources in the table */
    0, 0,   /* Reserved, must be 0 */
    { 0 },  /* Offsets to resources */
};

#endif /* _RSC_TABLE_PRU_H_ */
