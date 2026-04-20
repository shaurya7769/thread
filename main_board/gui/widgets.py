import sys, os, json, csv, time, random, subprocess
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ── Palette (Main UI Sync) ──────────────────────────────────────────────────
BG    = "#ECEFF4"
CARD  = "#FFFFFF"
NEON  = "#1B8A4C"
CYAN  = "#1565C0"
AMBER = "#C06000"
RED   = "#C62828"
MAGI  = "#5E35B1"
HEADER_BG     = "#1C2333" # Dark Navy from Screenshot
HEADER_ACCENT = "#2A3A50"

# ── Styles ──────────────────────────────────────────────────────────────────
SS = """
QWidget {
    background: #ECEFF4;
    color: #1A2332;
    font-family: 'Segoe UI', 'Inter', sans-serif;
}
QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #DDE3EA;
    border-radius: 12px;
}
QPushButton#START {
    background: #1B8A4C; color: white; border-radius: 6px; font-weight: bold; font-size: 11pt; padding: 6px 20px;
}
QPushButton#PAUSE {
    background: #E3EEFA; border: 1.5px solid #1565C0; border-radius: 6px; color: #1565C0; font-weight: bold; font-size: 11pt;
}
QPushButton#SECONDARY {
    background: #FFFFFF; border: 1.5px solid #1565C0; border-radius: 6px; color: #1565C0; font-weight: bold; font-size: 10pt;
}
"""

class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(75)
        self._time_txt = "--:--:--"
        self._bat_txt = "87%"
        self._sensor_ok = True
        
        tmr = QTimer(self)
        tmr.timeout.connect(self._tick)
        tmr.start(1000)
        self._tick()

    def _tick(self):
        self._time_txt = datetime.now().strftime("%H:%M:%S")
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()

        # Background
        p.fillRect(0, 0, W, H, QColor(HEADER_BG))
        
        # Placeholder Logo
        p.setBrush(QColor("#FFFFFF"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(10, 10, 55, 55)
        
        # Bottom Line
        p.fillRect(0, H - 2, W, 2, QColor(HEADER_ACCENT))

        cy = H // 2
        f_mono = QFont("Courier New", 12, QFont.Bold)
        f_title = QFont("Segoe UI", 16, QFont.Bold)

        # LTE Bars
        p.setPen(QColor("#4CAF50"))
        p.setFont(f_mono)
        p.drawText(160, 0, 100, H, Qt.AlignVCenter, "📶 LTE")

        # Sensor Dot
        dot_col = QColor("#4CAF50") if self._sensor_ok else QColor("#EF5350")
        p.setBrush(dot_col)
        p.drawEllipse(230, cy - 6, 12, 12)
        p.setPen(QColor("#A8C8A8"))
        p.drawText(250, 0, 120, H, Qt.AlignVCenter, "SENSOR OK")

        # Title (LWTMT)
        p.setPen(QColor("#F3F6FB"))
        p.setFont(f_title)
        p.drawText(0, 0, W, H, Qt.AlignCenter, "LWTMT")

        # Battery & Time
        p.setFont(f_mono)
        p.setPen(QColor("#FFFFFF"))
        p.drawText(W - 320, 0, 100, H, Qt.AlignVCenter | Qt.AlignRight, "▮ 87%")
        p.drawText(W - 200, 0, 180, H, Qt.AlignVCenter | Qt.AlignRight, self._time_txt)
        p.end()

class MetricCard(QFrame):
    def __init__(self, key, title, unit, color, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.color = color
        self.setStyleSheet(f"QFrame#Card {{ border-left: 6px solid {color}; }}")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 15, 20, 15)
        
        hdr = QHBoxLayout()
        t = QLabel(title.upper())
        t.setStyleSheet("color: #1A2332; font-size: 11pt; font-weight: bold; letter-spacing: 1px;")
        badge = QLabel("NOMINAL")
        badge.setStyleSheet(f"background: {color}15; color: {color}; border: 1px solid {color}; border-radius: 4px; font-size: 8pt; font-weight: bold; padding: 2px 8px;")
        hdr.addWidget(t)
        hdr.addStretch()
        hdr.addWidget(badge)
        lay.addLayout(hdr)
        
        lay.addStretch()
        
        val_lay = QHBoxLayout()
        self.val_lbl = QLabel("---")
        self.val_lbl.setStyleSheet(f"color: {color}; font-size: 52pt; font-weight: 800;")
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet("color: #8A94A6; font-size: 18pt; font-weight: bold;")
        unit_lbl.setAlignment(Qt.AlignBottom)
        
        val_lay.addStretch()
        val_lay.addWidget(self.val_lbl)
        val_lay.addWidget(unit_lbl)
        val_lay.addStretch()
        lay.addLayout(val_lay)
        lay.addStretch()

    def refresh(self, val):
        if isinstance(val, float):
            self.val_lbl.setText(f"{val:.2f}")
        else:
            self.val_lbl.setText(str(val))

def _btn(label, name, h=48, w=None):
    b = QPushButton(label)
    b.setObjectName(name)
    b.setFixedHeight(h)
    if w: b.setFixedWidth(w)
    return b
