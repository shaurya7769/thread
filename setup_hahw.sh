#!/bin/bash
# Master Setup Script: Rail Inspection HAHW Architecture (Optimized for Buster)
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
    pru-software-support-package || echo "Note: some PRU packages not in apt, continuing..."

# config-pin detection
if ! command -v config-pin &> /dev/null; then
    echo "config-pin not in PATH, checking /usr/bin..."
    if [ -f /usr/bin/config-pin ]; then
        alias config-pin='/usr/bin/config-pin'
    else
        echo "Installing beaglebone-universal-io..."
        sudo apt-get install -y beaglebone-universal-io || echo "Please install universal-io manually."
    fi
fi

# Ensure PRU headers are available
if [ ! -d "/usr/lib/ti/pru-software-support-package/include" ]; then
    echo "PRU headers not found. Cloning Software Support Package..."
    sudo mkdir -p /usr/lib/ti
    sudo git clone --depth 1 https://github.com/dinuxman/pru-software-support-package.git /usr/lib/ti/pru-software-support-package
fi

echo "---------------------------------------------------------"
echo "  2. Initializing Hardware Ports (SPI & GPIO)            "
echo "---------------------------------------------------------"
# Rotary Encoder Pins (P8.11, P8.12 are PRU0)
sudo config-pin P8_11 gpio
sudo config-pin P8_12 gpio
sudo config-pin P8_15 gpio

# SCL3300 SPI Pins
sudo config-pin P9_17 spi_cs
sudo config-pin P9_18 spi
sudo config-pin P9_21 spi
sudo config-pin P9_22 spi_sclk

echo "---------------------------------------------------------"
echo "  3. Building & Loading the Distributed Architecture      "
echo "---------------------------------------------------------"
cd sensor_board
make clean
make

# Copy firmware to standard location
# Based on P8.11/12, we target PRU0 (remoteproc0)
FW_DEST="/lib/firmware/am335x-pru0-fw"
sudo cp pru/encoder_pru.out $FW_DEST

# Detect remoteproc node for PRU0
REMOTELOC=$(ls /sys/class/remoteproc/ | grep remoteproc0 || ls /sys/class/remoteproc/ | head -n 1)

echo "Initializing PRU Core ($REMOTELOC)..."
# Force stop if running
if [ -f "/sys/class/remoteproc/$REMOTELOC/state" ]; then
    CURRENT_STATE=$(cat /sys/class/remoteproc/$REMOTELOC/state)
    if [ "$CURRENT_STATE" == "running" ]; then
        echo "stop" | sudo tee /sys/class/remoteproc/$REMOTELOC/state || true
        sleep 1
    fi
fi

echo "am335x-pru0-fw" | sudo tee /sys/class/remoteproc/$REMOTELOC/firmware || echo "Error setting firmware name"
sleep 1
echo "start" | sudo tee /sys/class/remoteproc/$REMOTELOC/state || echo "Error: Start failed. Make sure firmware exists in /lib/firmware"
cd ..

echo "---------------------------------------------------------"
echo "  4. Verification & Testing                              "
echo "---------------------------------------------------------"
PRU_STATE=$(cat /sys/class/remoteproc/$REMOTELOC/state)
echo "PRU STATUS: $PRU_STATE"

if [ "$PRU_STATE" == "running" ]; then
    echo "[SUCCESS] PRU firmware loaded and running."
else
    echo "[ERROR] PRU failed to start. Check 'dmesg | grep remoteproc'"
fi

echo "SETUP COMPLETE."
echo "---------------------------------------------------------"
echo "TERMINAL 1: sudo ./sensor_board/sensor_service"
echo "TERMINAL 2: python3 integrated_ui.py"
echo "---------------------------------------------------------"
