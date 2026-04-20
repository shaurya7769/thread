import csv
import os
import time
from datetime import datetime

class SurveyLogger:
    def __init__(self, base_dir="~/surveys"):
        self.base_dir = os.path.expanduser(base_dir)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        
        self.file_path = None
        self.csv_file = None
        self.writer = None
        self.active = False

    def start(self, station_name="SURVEY"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{station_name}_{timestamp}.csv"
        self.file_path = os.path.join(self.base_dir, filename)
        
        self.csv_file = open(self.file_path, mode='w', newline='')
        self.writer = csv.writer(self.csv_file)
        
        # Header
        self.writer.writerow([
            "Timestamp", "Distance_m", "Tilt_deg", 
            "Crosslevel_mm", "Twist_mm", "TwistRate_mmpm", "Status"
        ])
        
        self.active = True
        print(f"[LOG] Survey logging started: {self.file_path}")

    def log_packet(self, data):
        if not self.active or not self.writer:
            return
            
        try:
            self.writer.writerow([
                data.get('timestamp', time.time()),
                f"{data.get('distance', 0.0):.3f}",
                f"{data.get('tilt', 0.0):.3f}",
                f"{data.get('crosslevel', 0.0):.2f}",
                f"{data.get('twist', 0.0):.2f}",
                f"{data.get('twist_rate', 0.0):.2f}",
                data.get('status', 'OK')
            ])
            # Periodic flush to ensure data safety
            self.csv_file.flush()
        except Exception as e:
            print(f"[LOG] Write Error: {e}")

    def stop(self):
        if self.csv_file:
            self.csv_file.close()
        self.active = False
        self.writer = None
        print(f"[LOG] Survey logging stopped: {self.file_path}")
