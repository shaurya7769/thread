import socket
import struct
import threading
import time

# Packet format according to common.h:
# [Sync(I)|Seq(H)|TS(Q)|Dist(d)|Tilt(d)|Gauge(f)|CRC(B)|Status(B)]
# Total 36 bytes
PACKET_FMT = "<I H Q d d f B B"
PACKET_SIZE = struct.calcsize(PACKET_FMT)

class SensorClient(threading.Thread):
    def __init__(self, host="localhost", port=5060, callback=None):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.callback = callback
        self.running = True
        self.health_reported = False

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
                        if not data or len(data) < PACKET_SIZE:
                            break
                        
                        unpacked = struct.unpack(PACKET_FMT, data)
                        sync, seq, ts, dist, tilt, gauge, crc, status = unpacked
                        
                        if sync == 0x55AA55AA:
                            # Health Report on first packet
                            if not self.health_reported:
                                incl_ok = "OK" if status & 0x01 else "FAIL"
                                enco_ok = "OK" if status & 0x02 else "FAIL"
                                print(f"\n[HW] --- HARDWARE HEALTH SUMMARY ---")
                                print(f"[HW] Inclinometer (SCL3300): {incl_ok}")
                                print(f"[HW] Encoder (eQEP/PRU):    {enco_ok}")
                                print(f"[HW] -------------------------------\n")
                                self.health_reported = True

                            packet_dict = {
                                "seq": seq,
                                "status": status,
                                "timestamp": ts,
                                "distance": dist,
                                "tilt": tilt,
                                "gauge": gauge
                            }
                            if self.callback:
                                self.callback(packet_dict)
                        
            except Exception as e:
                print(f"[NET] Connection error: {e}")
                self.health_reported = False
                time.sleep(2)

    def stop(self):
        self.running = False
