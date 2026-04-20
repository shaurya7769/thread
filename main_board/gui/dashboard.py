from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from gui.widgets import *

# ─────────────────────────────────────────────────────────────────────────────
#  TOP BAR (Enhanced with EXIT Button)
# ─────────────────────────────────────────────────────────────────────────────
class TopBar(QWidget):
    sig_exit = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(75)
        self.setStyleSheet(f"background-color: {HEADER_BG}; border-bottom: 2px solid {NEON};")
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(15, 0, 25, 0)
        
        # Top-Left EXIT Button as requested
        self.exit_btn = QPushButton("EXIT")
        self.exit_btn.setFixedSize(90, 45)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #C62828; color: white; border-radius: 8px; font-weight: bold; font-size: 11pt;
            }
            QPushButton:pressed { background-color: #A00000; }
        """)
        self.exit_btn.clicked.connect(self.sig_exit.emit)
        
        title = QLabel("TRACK INSPECTION UNIT")
        title.setStyleSheet("color: white; font-size: 18pt; font-weight: 800; margin-left: 20px;")
        
        self.status_lbl = QLabel("SYSTEM: READY")
        self.status_lbl.setStyleSheet(f"color: {NEON}; font-size: 10pt; font-weight: bold; background: #0A2E1C; padding: 6px 15px; border-radius: 15px;")
        
        lay.addWidget(self.exit_btn)
        lay.addWidget(title)
        lay.addStretch()
        lay.addWidget(self.status_lbl)

# ─────────────────────────────────────────────────────────────────────────────
#  CONTROL BAR
# ─────────────────────────────────────────────────────────────────────────────
class ControlBar(QWidget):
    sig_start = pyqtSignal()
    sig_cal   = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(65)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        
        self.start_btn = _btn("▶ START SURVEY", "BG", 48, 180)
        self.cal_btn   = _btn("⚙ CALIBRATE", "BA", 48, 160)
        
        lay.addWidget(self.start_btn)
        lay.addSpacing(10)
        lay.addWidget(self.cal_btn)
        lay.addStretch()

# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD PAGE
# ─────────────────────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(15, 15, 15, 15)
        self.lay.setSpacing(15)
        
        # Metrics Grid (2x2 like main_ui.py)
        grid = QGridLayout()
        grid.setSpacing(15)
        self.cards = {
            'gauge':      MetricCard('gauge', 'Track Gauge', 'mm', NEON),
            'crosslevel': MetricCard('crosslevel', 'Cross Level', 'mm', CYAN),
            'twist':      MetricCard('twist', 'Twist (3m)', 'mm/m', AMBER),
            'distance':   MetricCard('distance', 'Distance', 'm', MAGI)
        }
        grid.addWidget(self.cards['gauge'], 0, 0)
        grid.addWidget(self.cards['crosslevel'], 0, 1)
        grid.addWidget(self.cards['twist'], 1, 0)
        grid.addWidget(self.cards['distance'], 1, 1)
        self.lay.addLayout(grid)

    def update_data(self, data):
        for k, card in self.cards.items():
            if k in data:
                card.refresh(data[k])

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN DASHBOARD CONTAINER
# ─────────────────────────────────────────────────────────────────────────────
class MainDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1024, 600)
        self.setStyleSheet(f"background-color: {BG};")
        
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)
        
        self.topbar = TopBar()
        self.page_stack = QStackedWidget()
        self.dash_page = DashboardPage()
        self.page_stack.addWidget(self.dash_page)
        
        self.ctrl_bar = ControlBar()
        
        self.lay.addWidget(self.topbar)
        self.lay.addWidget(self.page_stack, 1)
        self.lay.addWidget(self.ctrl_bar)
