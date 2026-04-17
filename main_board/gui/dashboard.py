import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Industrial Palette from Reference
BG_LIGHT      = "#ECEFF4"
CARD_BG       = "#FFFFFF"
BORDER        = "#DDE3EA"
HEADER_BG     = "#1E2430"
ACCENT_GREEN  = "#1B8A4C" # Gauge
ACCENT_BLUE   = "#1565C0" # Crosslevel
ACCENT_AMBER  = "#C06000" # Twist
ACCENT_VIOLET = "#5E35B1" # Distance
TEXT_MAIN     = "#1A2332"

class MetricCard(QFrame):
    def __init__(self, title, unit, accent_color, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER};
                border-left: 5px solid {accent_color};
                border-radius: 10px;
            }}
        """)
        self.setFixedHeight(140)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"color: #8A94A6; font-size: 11pt; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(title_lbl)
        
        val_layout = QHBoxLayout()
        self.val_lbl = QLabel("0.00")
        self.val_lbl.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 34pt; font-weight: 800;")
        
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet(f"color: #8A94A6; font-size: 14pt; font-weight: bold; margin-bottom: 5px;")
        unit_lbl.setAlignment(Qt.AlignBottom)
        
        val_layout.addWidget(self.val_lbl)
        val_layout.addStretch()
        val_layout.addWidget(unit_lbl)
        layout.addLayout(val_layout)

    def set_value(self, val):
        if isinstance(val, float):
            self.val_lbl.setText(f"{val:.2f}")
        else:
            self.val_lbl.setText(str(val))

class Dashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HAHW Rail Inspection")
        self.setFixedSize(1024, 600)
        self.setStyleSheet(f"background-color: {BG_LIGHT}; color: {TEXT_MAIN}; font-family: 'Segoe UI', Arial;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Top Header ---
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"background-color: {HEADER_BG}; border-bottom: 2px solid {ACCENT_GREEN};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(25, 0, 25, 0)
        
        title = QLabel("TWIST MODULE — HAHW ARCHITECTURE")
        title.setStyleSheet(f"color: white; font-size: 16pt; font-weight: bold; letter-spacing: 1.5px;")
        
        self.status_lbl = QLabel("SYSTEM: READY")
        self.status_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10pt; font-weight: bold; background: #0A2E1C; padding: 5px 12px; border-radius: 12px;")
        
        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(self.status_lbl)
        main_layout.addWidget(header)
        
        # --- Content Area ---
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(20)
        
        # Row 1: Primary Metrics
        metrics_row = QHBoxLayout()
        self.gauge_card = MetricCard("Track Gauge", "mm", ACCENT_GREEN)
        self.cl_card    = MetricCard("Cross Level", "mm", ACCENT_BLUE)
        self.dist_card  = MetricCard("Distance", "m", ACCENT_VIOLET)
        
        metrics_row.addWidget(self.gauge_card)
        metrics_row.addWidget(self.cl_card)
        metrics_row.addWidget(self.dist_card)
        content_layout.addLayout(metrics_row)
        
        # Row 2: Large Twist Display
        twist_row = QHBoxLayout()
        self.twist_card = MetricCard("Twist (3m Base)", "mm/m", ACCENT_AMBER)
        self.twist_card.setFixedHeight(180)
        self.twist_card.val_lbl.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 52pt; font-weight: 800;")
        
        # Diagnostic Terminal View (Industrial style)
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("""
            background-color: #10141D;
            color: #A0AEC0;
            border-radius: 8px;
            font-family: 'Consolas', monospace;
            font-size: 9pt;
            padding: 10px;
        """)
        self.terminal.setPlaceholderText("Hardware Diagnostic Output...")
        
        twist_row.addWidget(self.twist_card, 2)
        twist_row.addWidget(self.terminal, 3)
        content_layout.addLayout(twist_row)
        
        main_layout.addWidget(content)
        
    def update_data(self, data):
        """Standard update function for Sensor packets"""
        self.gauge_card.set_value(data['gauge'])
        self.cl_card.set_value(data['crosslevel'])
        self.dist_card.set_value(data['distance'])
        self.twist_card.set_value(data['twist_rate'])
        
        # Status coloring
        if data['status'] == 'ALARM':
            self.twist_card.setStyleSheet(self.twist_card.styleSheet().replace(ACCENT_AMBER, "#C62828"))
            self.status_lbl.setText("STATUS: TWIST ALARM")
            self.status_lbl.setStyleSheet(self.status_lbl.styleSheet().replace(ACCENT_GREEN, "#C62828").replace("#0A2E1C", "#2E0A0A"))
        else:
            self.twist_card.setStyleSheet(self.twist_card.styleSheet().replace("#C62828", ACCENT_AMBER))
            self.status_lbl.setText("STATUS: OPERATING")
            self.status_lbl.setStyleSheet(self.status_lbl.styleSheet().replace("#C62828", ACCENT_GREEN).replace("#2E0A0A", "#0A2E1C"))

        # Log to terminal (circular log)
        ts = data.get('timestamp', 0)
        log_entry = f"[{ts}] RX PKT: CL={data['crosslevel']:.2f} | TWIST={data['twist_rate']:.3f} | DIST={data['distance']:.3f}\n"
        self.terminal.append(log_entry)
        if self.terminal.blockCount() > 50:
            cursor = self.terminal.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()
