import socket
import struct
import threading
import time

# Packet format according to common.h:
# [Sync(2s)|Seq(H)|TS(Q)|Dist(d)|Tilt(d)|Gauge(f)|CRC(B)]
# Format: <HHQddfB (Little Endian)
PACKET_FMT = "<HHQddfB"
PACKET_SIZE = struct.calcsize(PACKET_FMT)

class SensorClient(threading.Thread):
    def __init__(self, host="localhost", port=5060, callback=None):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.callback = callback
        self.running = True

    def run(self):
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    print(f"[NET] Connecting to {self.host}:{self.port}...")
                    s.connect((self.host, self.port))
                    print("[NET] Connected to Sensor Board")
                    
                    while self.running:
                        data = s.recv(PACKET_SIZE)
                        if not data:
                            break
                        
                        if len(data) == PACKET_SIZE:
                            unpacked = struct.unpack(PACKET_FMT, data)
                            sync, seq, ts, dist, tilt, gauge, crc = unpacked
                            
                            if sync == 0xAA55:
                                packet_dict = {
                                    "seq": seq,
                                    "timestamp": ts,
                                    "distance": dist,
                                    "tilt": tilt,
                                    "gauge": gauge
                                }
                                if self.callback:
                                    self.callback(packet_dict)
                        
            except Exception as e:
                print(f"[NET] Connection error: {e}")
                time.sleep(2)

    def stop(self):
        self.running = False
