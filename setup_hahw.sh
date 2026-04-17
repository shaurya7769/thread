#!/bin/bash
# Master Setup Script: Rail Inspection HAHW Architecture
# Targets: BeagleBone Black (Debian/Ubuntu)

echo "---------------------------------------------------------"
echo "  1. Installing Dependencies (Libraries & PRU Support)   "
echo "---------------------------------------------------------"
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-pyqt5 \
    python3-requests \
    python3-pip \
    git \
    ti-pru-cgt \
    pru-software-support-package

# config-pin is often pre-installed or part of beaglebone-scripts
sudo apt-get install -y config-pin || echo "Note: config-pin not found in apt, checking if it exists..."

# Ensure PRU headers are available
if [ ! -d "/usr/lib/ti/pru-software-support-package/include" ]; then
    echo "PRU headers not found. Cloning Software Support Package..."
    sudo mkdir -p /usr/lib/ti
    sudo git clone --depth 1 https://github.com/dinuxman/pru-software-support-package.git /usr/lib/ti/pru-software-support-package
fi

echo "---------------------------------------------------------"
echo "  2. Initializing Hardware Ports (SPI & GPIO)            "
echo "---------------------------------------------------------"
# Rotary Encoder Pins
sudo config-pin P8_12 gpio    # Encoder A
sudo config-pin P8_11 gpio    # Encoder B
sudo config-pin P8_15 gpio    # Encoder Z

# SCL3300 SPI Pins
sudo config-pin P9_17 spi_cs
sudo config-pin P9_18 spi
sudo config-pin P9_21 spi
sudo config-pin P9_22 spi_sclk

echo "---------------------------------------------------------"
echo "  3. Updating Paths for Compiler (clpru)                 "
echo "---------------------------------------------------------"
# Add clpru to path if installed via apt
if [ -d /usr/share/ti/cgt-pru/bin ]; then
    export PATH=$PATH:/usr/share/ti/cgt-pru/bin
    export PRU_CGT=/usr/share/ti/cgt-pru
fi

echo "---------------------------------------------------------"
echo "  4. Building & Loading the Distributed Architecture      "
echo "---------------------------------------------------------"
cd sensor_board
make clean
make

# Copy firmware to standard location
sudo cp pru/encoder_pru.out /lib/firmware/am335x-pru1-fw

# Stop/Start PRU1 to load new firmware
echo "stop" | sudo tee /sys/class/remoteproc/remoteproc1/state || true
echo "am335x-pru1-fw" | sudo tee /sys/class/remoteproc/remoteproc1/firmware
echo "start" | sudo tee /sys/class/remoteproc/remoteproc1/state
cd ..

echo "---------------------------------------------------------"
echo "  5. Verification & Testing                              "
echo "---------------------------------------------------------"
PRU1_STATE=$(cat /sys/class/remoteproc/remoteproc1/state)
echo "PRU1 STATUS: $PRU1_STATE"

if [ "$PRU1_STATE" == "running" ]; then
    echo "[SUCCESS] PRU1 firmware loaded and running."
else
    echo "[ERROR] PRU1 failed to start."
fi

if [ -f "main_board/main.py" ]; then
    echo "[SUCCESS] Main Board Python application found."
else
    echo "[ERROR] Main Board found."
fi

echo ""
echo "SETUP COMPLETE."
echo "---------------------------------------------------------"
echo "TERMINAL 1: sudo ./sensor_board/sensor_service"
echo "TERMINAL 2: python3 main_board/main.py"
echo "---------------------------------------------------------"
