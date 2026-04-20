from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from network.tcp_client import SensorClient
from logic.calc_engine import CalculationEngine
from gui.dashboard import Dashboard

class RailApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # 1. Logic Engine
        self.logic = CalculationEngine(gauge_base=1676.0)
        
        # 2. UI Dashboard
        self.gui = Dashboard()
        self.gui.show()
        
        # Latest data state
        self.latest_processed = None
        
        # 3. UI Refresh Timer (30Hz = 33ms)
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.refresh_ui)
        self.ui_timer.start(33)
        
        # 4. Network Client (Receives at 100Hz)
        self.network = SensorClient(host="localhost", port=5060, callback=self.on_data)
        self.network.start()

    def on_data(self, raw_packet):
        """Callback from Network Thread (100Hz)"""
        # Process logic as fast as possible in network thread
        self.latest_processed = self.logic.process_packet(raw_packet)
        
    def refresh_ui(self):
        """Standard UI Refresh (30Hz)"""
        if self.latest_processed:
            self.gui.update_data(self.latest_processed)

    def run(self):
        try:
            sys.exit(self.app.exec_())
        except KeyboardInterrupt:
            self.network.stop()
            self.cloud.stop()

if __name__ == "__main__":
    app = RailApp()
    app.run()
