import sys, os, json, csv, time, random, subprocess
from datetime import datetime
from pathlib import Path
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError as e:
    print(f"[FATAL] PyQt5 missing: {e}")
    sys.exit(1)

# ── Palette ──────────────────────────────────────────────────────────────────
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

# ── Styles ──────────────────────────────────────────────────────────────────
SS = """
QWidget { background: #ECEFF4; color: #1A2332; font-family: sans-serif; }
QFrame#Card { background: white; border: 1px solid #DDE3EA; border-radius: 12px; }
QFrame#Panel { background: white; border: 1px solid #DDE3EA; border-radius: 10px; }
QPushButton#BG { background: #E6F4EE; border: 1.5px solid #1B8A4C; border-radius: 8px; color: #1B8A4C; font-weight: bold; font-size: 11pt; }
QPushButton#BA { background: #FFF3E0; border: 1.5px solid #C06000; border-radius: 8px; color: #C06000; font-weight: bold; font-size: 11pt; }
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
        self.setObjectName("Card")
        self.setStyleSheet(f"QFrame#Card {{ border-left: 5px solid {color}; }}")
        lay = QVBoxLayout(self)
        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet("color: #8A94A6; font-size: 10pt; font-weight: bold;")
        self.val_lbl = QLabel("0.00")
        self.val_lbl.setStyleSheet(f"color: {color}; font-size: 44pt; font-weight: 800;")
        lay.addWidget(self.title_lbl)
        lay.addWidget(self.val_lbl)

    def refresh(self, val):
        self.val_lbl.setText(f"{val:.2f}" if isinstance(val, float) else str(val))

class Stepper(QWidget):
    def __init__(self, val=0, unit="", parent=None):
        super().__init__(parent)
        self.lay = QHBoxLayout(self)
        self.btn = QPushButton(f"{val} {unit}")
        self.lay.addWidget(self.btn)

class StationParamsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("STATION PARAMETERS"))
