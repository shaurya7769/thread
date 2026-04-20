import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from network.tcp_client import SensorClient
from logic.calc_engine import CalculationEngine
from gui.dashboard import MainDashboard

class RailApp:
    def __init__(self):
        # Initialize QApplication first
        self.app = QApplication(sys.argv)
        
        # 1. Logic Engine
        self.logic = CalculationEngine(gauge_base=1676.0)
        
        # 2. UI Dashboard (Rich Portfolio Design)
        self.gui = MainDashboard()
        self.gui.topbar.sig_exit.connect(self.close_app)
        
        # Attempt full screen, fallback to normal if needed
        try:
            self.gui.showFullScreen()
        except:
            self.gui.show()
        
        # Latest data state
        self.latest_processed = None
        
        # 3. UI Refresh Timer (30Hz = 33ms)
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.refresh_ui)
        self.ui_timer.start(33)
        
        # 4. Network Client (Receives at 100Hz from C sensor_service)
        self.network = SensorClient(host="localhost", port=5060, callback=self.on_data)
        self.network.start()

    def on_data(self, raw_packet):
        """Callback from Network Thread (100Hz)"""
        # Process logic as fast as possible in network thread
        self.latest_processed = self.logic.process_packet(raw_packet)
        
    def refresh_ui(self):
        """Standard UI Refresh (30Hz)"""
        if self.latest_processed:
            # Pass data down to the richness dashboard pages
            self.gui.dash_page.update_data(self.latest_processed)

    def close_app(self):
        print("[APP] Shutting down...")
        self.network.stop()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = RailApp()
    app.run()
