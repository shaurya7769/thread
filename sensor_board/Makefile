CC = gcc
CFLAGS = -Wall -O2 -pthread
LIBS = -lpthread

# Auto-detect PRU CGT path
PRU_CGT ?= $(shell if [ -d /usr/share/ti/cgt-pru ]; then echo /usr/share/ti/cgt-pru; elif [ -d /usr/lib/ti/cgt-pru ]; then echo /usr/lib/ti/cgt-pru; else echo /usr; fi)
PRU_SSP ?= /usr/lib/ti/pru-software-support-package

# Point to standard PRU support headers (Buster/Trixie common paths)
PRU_INC = -I$(PRU_CGT)/include \
          -I$(PRU_SSP)/include \
          -I$(PRU_SSP)/include/am335x \
          -I/usr/include/pru

all: sensor_service pru_firmware

sensor_service: src/tcp_server.c src/acquisition.c
	$(CC) $(CFLAGS) -o sensor_service src/tcp_server.c src/acquisition.c $(LIBS) -lm

pru_firmware: pru/encoder_pru.c
	@echo "Checking for clpru..."
	@if command -v clpru >/dev/null 2>&1; then \
		clpru $(PRU_INC) -O2 pru/encoder_pru.c -z pru.cmd -o encoder_pru.out; \
	else \
		$(PRU_CGT)/bin/clpru $(PRU_INC) -O2 pru/encoder_pru.c -z pru.cmd -o encoder_pru.out || echo ">> Compilation failure"; \
	fi

clean:
	rm -f sensor_service
