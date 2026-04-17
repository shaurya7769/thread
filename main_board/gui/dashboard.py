import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

# Premium Industrial Palette
BG    = "#10141D"
CARD  = "#1E2430"
ACCENT= "#1B8A4C"
CYAN  = "#1565C0"
TEXT  = "#FFFFFF"
DIM   = "#8A94A6"

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rail Inspection System - HAHW Edition")
        self.setStyleSheet(f"background-color: {BG}; color: {TEXT}; font-family: 'DM Sans', sans-serif;")
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(15)

        # Header
        header = QHBoxLayout()
        title = QLabel("TRACK GEOMETRY INSPECTION")
        title.setFont(QFont("DM Sans", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        self.status_lbl = QLabel("SYSTEM ONLINE")
        self.status_lbl.setStyleSheet(f"color: {ACCENT}; font-weight: bold;")
        header.addWidget(self.status_lbl)
        root.addLayout(header)

        # Main Grid
        grid = QGridLayout()
        grid.setSpacing(15)

        self.dist_card = self.create_card("DISTANCE", "0.00", "m", grid, 0, 0)
        self.tilt_card = self.create_card("TILT", "0.00", "°", grid, 0, 1)
        self.cross_card = self.create_card("CROSSLEVEL", "0.0", "mm", grid, 1, 0)
        self.twist_card = self.create_card("TWIST (3m)", "0.00", "mm", grid, 1, 1)

        root.addLayout(grid)

        # Gauge Label (Static)
        gauge_box = QHBoxLayout()
        gauge_box.addWidget(QLabel("GAUGE SETTING:"))
        self.gauge_val = QLabel("1676.0 mm")
        self.gauge_val.setStyleSheet(f"color: {CYAN}; font-weight: bold;")
        gauge_box.addWidget(self.gauge_val)
        gauge_box.addStretch()
        root.addLayout(gauge_box)

    def create_card(self, title, val, unit, grid, r, c):
        f = QFrame()
        f.setStyleSheet(f"background-color: {CARD}; border-radius: 12px; border: 1px solid #2B3445;")
        l = QVBoxLayout(f)
        
        t = QLabel(title)
        t.setStyleSheet(f"color: {DIM}; font-size: 10pt; font-weight: bold;")
        l.addWidget(t)

        v_box = QHBoxLayout()
        v = QLabel(val)
        v.setStyleSheet(f"color: {TEXT}; font-size: 32pt; font-weight: bold; border: none;")
        u = QLabel(unit)
        u.setStyleSheet(f"color: {DIM}; font-size: 14pt; border: none;")
        v_box.addWidget(v)
        v_box.addWidget(u)
        v_box.addStretch()
        l.addLayout(v_box)

        grid.addWidget(f, r, c)
        return v

    def update_data(self, data):
        self.dist_card.setText(f"{data['distance']:.2f}")
        self.tilt_card.setText(f"{data['tilt']:.2f}")
        self.cross_card.setText(f"{data['cross_level']:.1f}")
        self.twist_card.setText(f"{data['twist_3m']:.2f}")
        
        # Color coding for thresholds
        if abs(data['twist_3m']) > 3.0:
            self.twist_card.setStyleSheet("color: #C62828; font-size: 32pt; font-weight: bold;")
        else:
            self.twist_card.setStyleSheet(f"color: {TEXT}; font-size: 32pt; font-weight: bold;")
