CC = gcc
CFLAGS = -Wall -O2 -pthread -D_DEFAULT_SOURCE
LIBS = -lpthread -lrt
PRU_CGT = /usr/share/ti/cgt-pru
PRU_SSP = /usr/lib/ti/pru-software-support-package

# Detection fallback for clpru
CLPRU = $(shell if [ -f $(PRU_CGT)/bin/clpru ]; then echo $(PRU_CGT)/bin/clpru; else echo clpru; fi)

# Only include PRU paths if they exist to avoid confusing clpru
PRU_INC = -I.
ifneq ($(wildcard $(PRU_CGT)/include),)
    PRU_INC += -I$(PRU_CGT)/include
endif
ifneq ($(wildcard $(PRU_SSP)/include),)
    PRU_INC += -I$(PRU_SSP)/include
    PRU_INC += -I$(PRU_SSP)/include/am335x
endif

TARGET = sensor_service
OBJS = src/tcp_server.o src/acquisition.o

all: $(TARGET) pru_firmware

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS) -lm

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

pru_firmware: pru/encoder_pru.c
	@echo "Building PRU firmware..."
	# Compile
	$(CLPRU) $(PRU_INC) -v3 -O2 -c pru/encoder_pru.c --obj_directory=pru/
	# Link with explicit entry point and retain settings
	$(CLPRU) -z pru/encoder_pru.obj pru/pru.cmd -o pru/encoder_pru.out --entry_point=main --warn_sections --diag_warning=225

clean:
	rm -f $(TARGET) src/*.o pru/*.obj pru/*.out
