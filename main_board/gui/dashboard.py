try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    pass

# Try to import widgets from the same package
try:
    from gui.widgets import *
except ImportError:
    try:
        from widgets import *
    except ImportError:
        print("[ERROR] Could not import widgets.py")

class TopBar(QWidget):
    sig_exit = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(75)
        self.setStyleSheet(f"background-color: {HEADER_BG}; border-bottom: 2px solid {NEON};")
        lay = QHBoxLayout(self)
        self.exit_btn = QPushButton("EXIT")
        self.exit_btn.setFixedSize(90, 45)
        self.exit_btn.setStyleSheet("background: #C62828; color: white; border-radius: 8px; font-weight: bold;")
        self.exit_btn.clicked.connect(self.sig_exit.emit)
        title = QLabel("TRACK INSPECTION UNIT")
        title.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; margin-left: 15px;")
        lay.addWidget(self.exit_btn)
        lay.addWidget(title)
        lay.addStretch()

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        grid = QGridLayout()
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
        lay.addLayout(grid)

    def update_data(self, data):
        for k, card in self.cards.items():
            if k in data: card.refresh(data[k])

class MainDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1024, 600)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0,0,0,0)
        self.topbar = TopBar()
        self.page_stack = QStackedWidget()
        self.dash_page = DashboardPage()
        self.page_stack.addWidget(self.dash_page)
        lay.addWidget(self.topbar)
        lay.addWidget(self.page_stack, 1)
