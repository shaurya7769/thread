CC = gcc
CFLAGS = -Wall -O2 -pthread
LIBS = -lpthread

# Auto-detect PRU CGT path
PRU_CGT ?= $(shell if [ -d /usr/share/ti/cgt-pru ]; then echo /usr/share/ti/cgt-pru; else echo /usr/lib/ti/cgt-pru; fi)
PRU_INC = $(PRU_CGT)/include

all: sensor_service pru_firmware

sensor_service: src/tcp_server.c src/acquisition.c
	$(CC) $(CFLAGS) -o sensor_service src/tcp_server.c src/acquisition.c $(LIBS) -lm

pru_firmware: pru/encoder_pru.c
	@echo "Checking for clpru..."
	@if command -v clpru >/dev/null 2>&1; then \
		clpru --include_path=$(PRU_INC) -O2 pru/encoder_pru.c -z pru.cmd -o encoder_pru.out; \
	else \
		echo "clpru not in PATH. Trying $(PRU_CGT)/bin/clpru..."; \
		$(PRU_CGT)/bin/clpru --include_path=$(PRU_INC) -O2 pru/encoder_pru.c -z pru.cmd -o encoder_pru.out || echo "Warning: clpru not found. PRU firmware not built."; \
	fi

clean:
	rm -f sensor_service
