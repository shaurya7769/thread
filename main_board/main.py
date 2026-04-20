import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from network.tcp_client import SensorClient
from logic.calc_engine import CalculationEngine
from gui.dashboard import MainDashboard
from cloud.uploader import upload_latest_csv

class RailApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # 1. Logic & Connectivity
        self.logic = CalculationEngine(gauge_base=1676.0)
        self.latest_processed = None
        
        # 2. Premium Industrial UI
        self.gui = MainDashboard()
        self.gui.showFullScreen()
        
        # UI Signals
        self.gui.btn_start.clicked.connect(self.start_survey)
        self.gui.btn_pause.clicked.connect(self.pause_survey)
        
        # 3. Network Thread (100Hz Sensor Stream)
        self.network = SensorClient(host="localhost", port=5060, callback=self.on_data)
        self.network.start()
        
        # 4. Refresh Loop (30Hz UI update)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_ui)
        self.timer.start(33)

    def on_data(self, packet):
        """Processes real-time sensor packets in the background thread."""
        self.latest_processed = self.logic.process_packet(packet)

    def refresh_ui(self):
        """Updates the dashboard metrics periodically."""
        if self.latest_processed:
            self.gui.dash_page.update_data(self.latest_processed)

    def start_survey(self):
        print("[APP] Survey Started.")
        self.gui.topbar.update() # Placeholder for survey state

    def pause_survey(self):
        print("[APP] Survey Paused.")

    def close_app(self):
        """Handles graceful termination and automated cloud upload."""
        print("[APP] Shutting down...")
        self.network.stop()
        
        # Execute automated cloud upload to 10.18.31.129 in background
        print("[CLOUD] Triggering automated CSV upload to cloud...")
        upload_latest_csv()
        
        self.app.quit()

    def run(self):
        # Override close button signal for uploader
        self.app.aboutToQuit.connect(self.close_app)
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = RailApp()
    app.run()
