import sys, os, json, csv, time, random, subprocess
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ── Palette (Exact Main UI Sync) ───────────────────────────────────────────
BG    = "#ECEFF4"
CARD  = "#FFFFFF"
NEON  = "#1B8A4C"  # GAUGE
CYAN  = "#1565C0"  # CROSSLEVEL
AMBER = "#C06000"  # TWIST
RED   = "#C62828"
MAGI  = "#5E35B1"  # DISTANCE
HEADER_BG     = "#1E2430" 
HEADER_ACCENT = "#1B8A4C"

# ── Styles ──────────────────────────────────────────────────────────────────
SS = """
QWidget {
    background: #ECEFF4;
    color: #1A2332;
    font-family: 'Segoe UI', 'Inter', 'Liberation Sans', sans-serif;
}
QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #DDE3EA;
    border-left: 4px solid #1B8A4C;
    border-radius: 10px;
}
"""

class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        self._time_txt = "--:--:--"
        self._bat_txt = "87%"
        self._sensor_ok = True
        self._bar_count = 4
        
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

        p.fillRect(0, 0, W, H, QColor("#1C2333"))
        
        # Logo Placeholder
        p.setBrush(QColor("#FFFFFF"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(10, 5, 60, 60)
        
        p.fillRect(0, H - 2, W, 2, QColor("#2A3A50"))

        cy = H // 2
        f_mono = QFont("Courier New", 12, QFont.Bold)
        f_title = QFont("Segoe UI", 16, QFont.Bold)

        # Signal bars logic from main_ui.py
        bw, bg_gap = 6, 4
        bar_hs = (7, 12, 17, 22)
        x = 220
        for i, bh in enumerate(bar_hs):
            by = cy + 9 - bh
            col = QColor("#4CAF50") if i < self._bar_count else QColor("#3A4555")
            path = QPainterPath()
            path.addRoundedRect(x, by, bw, bh, 1, 1)
            p.fillPath(path, col)
            x += bw + bg_gap

        p.setFont(f_mono)
        p.setPen(QColor("#4CAF50"))
        p.drawText(x + 4, 0, 100, H, Qt.AlignVCenter, "LTE")

        # Sensor Dot
        dot_col = QColor("#4CAF50") if self._sensor_ok else QColor("#EF5350")
        p.setBrush(dot_col)
        p.drawEllipse(x + 60, cy - 6, 12, 12)
        p.setPen(QColor("#A8C8A8"))
        p.drawText(x + 80, 0, 120, H, Qt.AlignVCenter, "SENSOR OK")

        # Title
        p.setFont(f_title)
        p.setPen(QColor("#F3F6FB"))
        p.drawText(QRect(80, 0, W-80, H), Qt.AlignCenter, "LWTMT")

        # Battery & Time
        p.setFont(f_mono)
        p.setPen(QColor("#FFFFFF"))
        right_offset = 20
        p.drawText(W - 140 - right_offset, 0, 140, H, Qt.AlignVCenter | Qt.AlignRight, self._time_txt)
        p.setPen(QColor("#A8C8A8"))
        p.drawText(W - 270 - right_offset, 0, 120, H, Qt.AlignVCenter | Qt.AlignRight, "▮ " + self._bat_txt)
        p.end()

class MetricCard(QFrame):
    def __init__(self, key, title, unit, color, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.color = color
        
        # Shadow effect
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        fx = QGraphicsDropShadowEffect(self)
        fx.setBlurRadius(16)
        fx.setOffset(0, 4)
        fx.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(fx)
        
        self.setStyleSheet(
            f"QFrame#Card {{ background:#FFFFFF; border:1px solid #DDE3EA; border-left:4px solid {color}; border-radius:10px; }}")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 6)
        lay.setSpacing(0)
        
        hdr = QWidget()
        hdr_l = QHBoxLayout(hdr)
        hdr_l.setContentsMargins(18, 10, 14, 8)
        
        t = QLabel(title.upper())
        t.setStyleSheet(f"color: #4A5568; font-size: 11pt; font-weight: 600; background: transparent;")
        badge = QLabel("NOMINAL")
        
        # Badge style map
        _BG_MAP = {
            "#1B8A4C": ("#D4EDDA", "#1B8A4C"),
            "#1565C0": ("#D0E4F7", "#1565C0"),
            "#C06000": ("#FFE8C0", "#944800"),
            "#5E35B1": ("#E0D4F5", "#5E35B1"),
        }
        bg, fg = _BG_MAP.get(color, ("#E8E8E8", "#333333"))
        badge.setStyleSheet(f"background: {bg}; color: {fg}; border: 1.5px solid {fg}; border-radius: 4px; font-size: 9pt; font-weight: bold; padding: 2px 10px; font-family: 'Courier New';")
        
        hdr_l.addWidget(t)
        hdr_l.addStretch()
        hdr_l.addWidget(badge)
        lay.addWidget(hdr)
        
        rule = QFrame()
        rule.setFixedHeight(1)
        rule.setStyleSheet("background:#DDE3EA; border:none;")
        lay.addWidget(rule)
        
        lay.addStretch()
        
        val_lay = QHBoxLayout()
        self.val_lbl = QLabel("---")
        self.val_lbl.setStyleSheet(f"color: {color}; font-size: 84pt; font-weight: 700; letter-spacing: -3px; background: transparent;")
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet("color: #8A94A6; font-size: 26pt; font-weight: 500; font-family: 'Courier New'; padding-bottom: 14px; background: transparent;")
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
