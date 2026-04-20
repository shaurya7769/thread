#!/bin/bash
# Master Setup Script: Rail Inspection HAHW Architecture (Final Optimized)
# Targets: BeagleBone Black (Debian/Ubuntu)

echo "---------------------------------------------------------"
echo "  1. Installing Dependencies (Libraries & PRU Support)   "
echo "---------------------------------------------------------"
sudo apt-get update
sudo apt-get install -y build-essential python3-pyqt5 python3-pip git pru-software-support-package || true

# Config-pin robust setup
CONFIG_PIN=$(which config-pin || echo "/usr/bin/config-pin")
if [ ! -f "$CONFIG_PIN" ]; then
    echo "Installing beaglebone-universal-io..."
    sudo apt-get install -y beaglebone-universal-io || true
fi

echo "---------------------------------------------------------"
echo "  2. Initializing Hardware Ports (SPI & GPIO)            "
echo "---------------------------------------------------------"
# Rotary Encoder Pins (P8.11, P8.12 set to QEP mode for hardware decoding)
sudo $CONFIG_PIN P8_11 qep
sudo $CONFIG_PIN P8_12 qep
sudo $CONFIG_PIN P8_15 gpio

# SCL3300 SPI Pins
sudo $CONFIG_PIN P9_17 spi_cs
sudo $CONFIG_PIN P9_18 spi
sudo $CONFIG_PIN P9_21 spi
sudo $CONFIG_PIN P9_22 spi_sclk

echo "---------------------------------------------------------"
echo "  3. Building & Loading the Distributed Architecture      "
echo "---------------------------------------------------------"
cd sensor_board
make clean
make

# Identify the correct remoteproc node for PRU0 (4a334000.pru)
REMOTELOC=""
for dir in /sys/class/remoteproc/remoteproc*; do
    if [ -f "$dir/name" ]; then
        NAME=$(cat "$dir/name")
        if [[ "$NAME" == *"4a334000.pru"* ]]; then
            REMOTELOC=$(basename "$dir")
            break
        fi
    fi
done

if [ -z "$REMOTELOC" ]; then
    echo "[ERROR] Could not find PRU0 (4a334000.pru) in /sys/class/remoteproc/"
    exit 1
fi

echo "Targeting PRU0 on $REMOTELOC..."

# Copy firmware to standard location
FW_NAME="am335x-pru0-fw"
sudo cp pru/encoder_pru.out /lib/firmware/$FW_NAME

# Load and Start
echo "Initializing PRU Core ($REMOTELOC)..."
if [ -f "/sys/class/remoteproc/$REMOTELOC/state" ]; then
    # Use sudo tee for permissions
    echo "stop" | sudo tee /sys/class/remoteproc/$REMOTELOC/state > /dev/null || true
    sleep 1
    echo "$FW_NAME" | sudo tee /sys/class/remoteproc/$REMOTELOC/firmware > /dev/null
    sleep 1
    echo "start" | sudo tee /sys/class/remoteproc/$REMOTELOC/state > /dev/null
fi
cd ..

echo "---------------------------------------------------------"
echo "  4. LTE Modem Configuration (Quectel EC200U-CN)         "
echo "---------------------------------------------------------"
# Force Airtel APN: airtelgprs.com
APN="airtelgprs.com"
echo "Configuring modem for Airtel (APN: $APN)..."

# Use nmcli if available, otherwise fallback to AT commands via chat
if command -v nmcli >/dev/null 2>&1; then
    sudo nmcli con delete Airtel 2>/dev/null || true
    sudo nmcli con add type gsm ifname "*" con-name Airtel apn $APN
    sudo nmcli con up Airtel 2>/dev/null || echo "[WARN] nmcli could not bring up modem. Checking state..."
else
    echo "nmcli missing. Ensure NetworkManager is installed for robust cellular handling."
fi

echo "---------------------------------------------------------"
echo "  5. Verification & Testing                              "
echo "---------------------------------------------------------"
PRU_STATE=$(cat /sys/class/remoteproc/$REMOTELOC/state)
echo "PRU STATUS: $PRU_STATE"
ip addr show | grep -E "ppp|wwan|eth" || echo "[WARN] No active cellular interface found."

echo "SETUP COMPLETE."
echo "---------------------------------------------------------"
echo "TERMINAL 1: sudo ./sensor_board/sensor_service"
echo "TERMINAL 2: sudo python3 main_board/main.py"
echo "---------------------------------------------------------"
