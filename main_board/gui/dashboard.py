from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .widgets import *

def _btn_factory(label, h=52, w=120, ss=""):
    b = QPushButton(label)
    b.setFixedHeight(h)
    if w: b.setFixedWidth(w)
    if ss: b.setStyleSheet(ss)
    return b

def get_ss_p(color, bg_color):
    return (
        f"QPushButton{{ background:{bg_color}; border:2px solid {color};"
        f" border-radius:8px; color:{color}; font-size:12pt; font-weight:bold; padding:0 16px; }}"
        f"QPushButton:pressed{{ background:{color}; color:#FFFFFF; }}"
    )

# ── DASHBOARD PAGE ──────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#ECEFF4;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 4)
        lay.setSpacing(4)
        
        grid = QGridLayout()
        grid.setSpacing(8)
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
        lay.addLayout(grid, 1)
        
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background:#DDE3EA; border:none;")
        lay.addWidget(sep)
        
        # Bottom controls from main_ui.py
        bot_w = QWidget()
        bot_w.setFixedHeight(62)
        bot = QHBoxLayout(bot_w)
        bot.setContentsMargins(4, 4, 4, 4)
        bot.setSpacing(10)
        
        ss_start = f"QPushButton{{ background:{NEON}; border:2px solid {NEON}; border-radius:8px; color:#FFFFFF; font-size:12pt; font-weight:bold; }}"
        ss_pause = get_ss_p(CYAN, "#E3EEFA")
        ss_entry = get_ss_p(CYAN, "#E3EEFA")
        ss_cal   = get_ss_p(AMBER, "#FFF3E0")
        
        self.btn_start = _btn_factory("▶  START", 52, 120, ss_start)
        self.btn_pause = _btn_factory("⏸  PAUSE", 52, 120, ss_pause)
        self.btn_entry = _btn_factory("DATA ENTRY", 52, 130, ss_entry)
        self.btn_cal   = _btn_factory("CALIBRATE", 52, 120, ss_cal)
        
        self.stat_lbl = QLabel("○  IDLE  0 pts")
        self.stat_lbl.setStyleSheet("color:#8A94A6; font-family:'Courier New'; font-size:10pt; font-weight:500;")
        
        bot.addStretch()
        bot.addWidget(self.btn_start)
        bot.addWidget(self.btn_pause)
        
        vsep = QFrame()
        vsep.setFixedSize(1, 36)
        vsep.setStyleSheet("background:#DDE3EA; border:none;")
        bot.addWidget(vsep)
        
        bot.addWidget(self.btn_entry)
        bot.addWidget(self.btn_cal)
        bot.addSpacing(8)
        bot.addWidget(self.stat_lbl)
        bot.addStretch()
        
        lay.addWidget(bot_w)

    def update_data(self, data):
        for k, card in self.cards.items():
            if k in data:
                card.refresh(data[k])

# ── DATA ENTRY PAGE ───────────────────────────────────────────────────────────
class DataEntryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(15, 10, 15, 15)
        
        title = QLabel("SURVEY DATA ENTRY")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1565C0; font-size: 14pt; font-weight: 800; margin-bottom: 5px;")
        self.lay.addWidget(title)
        
        panels = QHBoxLayout()
        panels.setSpacing(15)
        
        for name in ["STATION PARAMETERS", "GAUGE FREQUENCY", "TWIST PARAMETERS"]:
            p = QFrame(); p.setObjectName("Panel")
            p.setStyleSheet("QFrame#Panel { background:#FFFFFF; border:1px solid #DDE3EA; border-radius:10px; }")
            p_lay = QVBoxLayout(p)
            p_lay.addWidget(QLabel(name))
            p_lay.addStretch()
            panels.addWidget(p, 1)
            
        self.lay.addLayout(panels)

# ── MAIN DASHBOARD CONTAINER ─────────────────────────────────────────────────
class MainDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1024, 600)
        
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)
        
        self.topbar = TopBar()
        self.page_stack = QStackedWidget()
        
        self.dash_page = DashboardPage()
        self.entry_page = DataEntryPage()
        
        self.page_stack.addWidget(self.dash_page)
        self.page_stack.addWidget(self.entry_page)
        
        self.lay.addWidget(self.topbar)
        self.lay.addWidget(self.page_stack, 1)
        
        # Signals
        self.btn_start = self.dash_page.btn_start
        self.btn_pause = self.dash_page.btn_pause
        self.btn_entry = self.dash_page.btn_entry
        self.btn_cal   = self.dash_page.btn_cal
        
        self.btn_entry.clicked.connect(self._toggle_page)

    def _toggle_page(self):
        cur = self.page_stack.currentIndex()
        self.page_stack.setCurrentIndex(1 - cur)
        self.btn_entry.setText("DASHBOARD" if cur == 0 else "DATA ENTRY")
