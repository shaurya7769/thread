import sys
from PyQt5.QtWidgets import QApplication
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
        
        # 3. Network Client
        self.network = SensorClient(host="localhost", port=5060, callback=self.on_data)
        self.network.start()

    def on_data(self, raw_packet):
        """Callback from Network Thread"""
        # Process through logic engine
        processed = self.logic.process_packet(raw_packet)
        
        # Update UI
        self.gui.update_data(processed)

    def run(self):
        try:
            sys.exit(self.app.exec_())
        except KeyboardInterrupt:
            self.network.stop()
            self.cloud.stop()

if __name__ == "__main__":
    app = RailApp()
    app.run()
