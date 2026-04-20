from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from gui.widgets import *

# ── DASHBOARD PAGE (2x2 Grid) ────────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(15, 15, 15, 15)
        self.lay.setSpacing(15)
        
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

# ── DATA ENTRY PAGE (3 Panels) ───────────────────────────────────────────────
class DataEntryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(15, 10, 15, 15)
        
        title = QLabel("SURVEY DATA ENTRY")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1565C0; font-size: 14pt; font-weight: 800; letter-spacing: 2px; margin-bottom: 5px;")
        self.lay.addWidget(title)
        
        panels = QHBoxLayout()
        panels.setSpacing(15)
        
        # Panel 1: Station Params
        p1 = QFrame(); p1.setObjectName("Panel")
        p1_lay = QVBoxLayout(p1)
        p1_lay.addWidget(QLabel("STATION PARAMETERS"))
        p1_lay.addStretch()
        panels.addWidget(p1, 1)
        
        # Panel 2: Gauge Params
        p2 = QFrame(); p2.setObjectName("Panel")
        p2_lay = QVBoxLayout(p2)
        p2_lay.addWidget(QLabel("GAUGE FREQUENCY"))
        p2_lay.addStretch()
        panels.addWidget(p2, 1)
        
        # Panel 3: Twist Params
        p3 = QFrame(); p3.setObjectName("Panel")
        p3_lay = QVBoxLayout(p3)
        p3_lay.addWidget(QLabel("TWIST PARAMETERS"))
        p3_lay.addStretch()
        panels.addWidget(p3, 1)
        
        self.lay.addLayout(panels)

# ── MAIN DASHBOARD CONTAINER ─────────────────────────────────────────────────
class MainDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1024, 600)
        self.setStyleSheet(SS)
        
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)
        
        self.topbar = TopBar()
        self.page_stack = QStackedWidget()
        
        self.dash_page = DashboardPage()
        self.entry_page = DataEntryPage()
        
        self.page_stack.addWidget(self.dash_page)
        self.page_stack.addWidget(self.entry_page)
        
        # Bottom Bar
        self.bot_bar = QWidget()
        self.bot_bar.setFixedHeight(55)
        self.bot_bar.setStyleSheet("background: #E8EEF4; border-top: 1px solid #DDE3EA;")
        bot_lay = QHBoxLayout(self.bot_bar)
        bot_lay.setContentsMargins(20, 0, 20, 0)
        
        self.btn_start = _btn("▶ START", "START", 38, 120)
        self.btn_pause = _btn("⏸ PAUSE", "PAUSE", 38, 120)
        self.btn_entry = _btn("DATA ENTRY", "SECONDARY", 38, 140)
        self.btn_cal   = _btn("CALIBRATE", "SECONDARY", 38, 140)
        
        bot_lay.addStretch()
        bot_lay.addWidget(self.btn_start)
        bot_lay.addWidget(self.btn_pause)
        bot_lay.addWidget(self.btn_entry)
        bot_lay.addWidget(self.btn_cal)
        bot_lay.addStretch()
        
        self.lay.addWidget(self.topbar)
        self.lay.addWidget(self.page_stack, 1)
        self.lay.addWidget(self.bot_bar)
        
        # Wire Page Switching
        self.btn_entry.clicked.connect(self._toggle_page)

    def _toggle_page(self):
        cur = self.page_stack.currentIndex()
        self.page_stack.setCurrentIndex(1 - cur)
        self.btn_entry.setText("DASHBOARD" if cur == 0 else "DATA ENTRY")
