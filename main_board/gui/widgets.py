import sys, os, json, csv, time, random, subprocess
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ─────────────────────────────────────────────────────────────────────────────
#  PALETTE
# ─────────────────────────────────────────────────────────────────────────────
BG    = "#ECEFF4"
CARD  = "#FFFFFF"
NEON  = "#1B8A4C"
CYAN  = "#1565C0"
AMBER = "#C06000"
RED   = "#C62828"
MAGI  = "#5E35B1"
HEADER_BG     = "#1E2430"
HEADER_ACCENT = "#1B8A4C"

NEON_LT  = "#E6F4EE"
CYAN_LT  = "#E3EEFA"
AMBER_LT = "#FFF3E0"
MAGI_LT  = "#EDE7F6"
RED_LT   = "#FFEBEE"
WARN     = "#E65100"
WARN_LT  = "#FFF3E0"

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL STYLESHEET
# ─────────────────────────────────────────────────────────────────────────────
SS = """
QWidget {
    background: #ECEFF4;
    color: #1A2332;
    font-family: 'Inter', 'DM Sans', 'Liberation Sans', sans-serif;
}
QDialog { background: #FFFFFF; }
QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #DDE3EA;
    border-left: 4px solid #1B8A4C;
    border-radius: 10px;
}
QFrame#Panel {
    background: #FFFFFF;
    border: 1px solid #DDE3EA;
    border-radius: 8px;
}
QTextEdit {
    background: #FFFFFF;
    border: 1px solid #DDE3EA;
    color: #1A2332;
    font-size: 8pt;
    font-family: 'Roboto Mono', 'Courier New';
}
QScrollBar:vertical          { background: #ECEFF4; width: 32px; }
QScrollBar::handle:vertical  { background: #C8D0DA; border-radius: 16px; min-height: 40px; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }

QPushButton#BG {
    background: #E6F4EE; border: 1.5px solid #1B8A4C;
    border-radius: 6px; color: #1B8A4C;
    font-size: 10pt; font-weight: bold;
}
QPushButton#BC {
    background: #FFFFFF; border: 2px solid #1565C0;
    border-radius: 12px; color: #1565C0;
    font-size: 10pt; font-weight: 700;
    padding: 4px 18px;
    min-height: 34px;
}
QPushButton#BA {
    background: #FFF3E0; border: 1.5px solid #C06000;
    border-radius: 6px; color: #C06000;
    font-size: 10pt; font-weight: bold;
}
"""

def _lbl(text, color="#888", pt=9, bold=False):
    l = QLabel(text)
    w = "bold" if bold else "normal"
    l.setStyleSheet(f"color:{color}; font-size:{pt}pt; font-weight:{w};")
    l.setWordWrap(True)
    return l

def _btn(label, name, h=48, w=None):
    b = QPushButton(label)
    b.setObjectName(name)
    b.setFixedHeight(h)
    if w: b.setFixedWidth(w)
    return b

class MetricCard(QFrame):
    def __init__(self, key, title, unit, color, parent=None):
        super().__init__(parent)
        self.key   = key
        self.color = color
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        
        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet(f"color: #8A94A6; font-size: 10pt; font-weight: bold; letter-spacing: 1px;")
        lay.addWidget(self.title_lbl)
        
        val_lay = QHBoxLayout()
        self.val_lbl = QLabel("0.00")
        self.val_lbl.setStyleSheet(f"color: {color}; font-size: 48pt; font-weight: 800;")
        
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet(f"color: #8A94A6; font-size: 16pt; font-weight: bold;")
        unit_lbl.setAlignment(Qt.AlignBottom)
        
        val_lay.addWidget(self.val_lbl)
        val_lay.addStretch()
        val_lay.addWidget(unit_lbl)
        lay.addLayout(val_lay)
        
        self.setStyleSheet(f"QFrame#Card {{ background: white; border-left: 5px solid {color}; border-radius: 12px; border: 1px solid #DDE3EA; }}")

    def refresh(self, val):
        if isinstance(val, float):
            self.val_lbl.setText(f"{val:.2f}")
        else:
            self.val_lbl.setText(str(val))

class Stepper(QWidget):
    changed = pyqtSignal(float)
    def __init__(self, val=0, step=1, dec=0, lo=0, hi=9999, unit="", title="VALUE", parent=None):
        super().__init__(parent)
        self._val = float(val); self._dec = dec
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.btn = QPushButton(f"{self._val:.{self._dec}f} {unit}")
        self.btn.setFixedHeight(44)
        self.btn.setStyleSheet("QPushButton { background: white; border: 1px solid #C8D0DA; border-radius: 8px; font-weight: bold; }")
        self.lay.addWidget(self.btn)
    def value(self): return self._val

class StationParamsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.lay = QVBoxLayout(self)
        self.lay.addWidget(QLabel("STATION PARAMETERS"))
        self.lay.addStretch()
