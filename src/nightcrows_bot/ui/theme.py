APP_STYLE = """
QWidget {
    background: #10141d;
    color: #e8ecf4;
    font-family: "Segoe UI";
    font-size: 13px;
}
QMainWindow { background: #0b0f16; }
QLabel, QCheckBox { background: transparent; }
QFrame#Sidebar, QFrame#Panel {
    background: #161c27;
    border: 1px solid #273143;
    border-radius: 14px;
}
QLabel#Title { font-size: 24px; font-weight: 700; color: #f5c76b; }
QLabel#Subtitle { color: #8f9bad; }
QLabel#Section { font-size: 15px; font-weight: 650; color: #f4f6fa; }
QLabel#StatusBadge {
    background: #232b39;
    color: #aeb8c8;
    border-radius: 10px;
    padding: 7px 11px;
    font-weight: 650;
}
QComboBox, QSpinBox {
    background: #0e131c;
    border: 1px solid #303b50;
    border-radius: 8px;
    padding: 8px;
    min-height: 20px;
}
QComboBox:focus, QSpinBox:focus { border-color: #d5a84d; }
QPushButton {
    background: #252e3d;
    border: 1px solid #354156;
    border-radius: 9px;
    padding: 10px 16px;
    font-weight: 650;
}
QPushButton:hover { background: #303b4e; }
QPushButton#Primary {
    background: #d3a74d;
    color: #11151d;
    border: none;
}
QPushButton#Primary:hover { background: #e4bb67; }
QPushButton#Danger { background: #46232a; border-color: #74313c; color: #ffb5bf; }
QPushButton:disabled { color: #657084; background: #1a202b; }
QCheckBox { spacing: 9px; }
QCheckBox::indicator { width: 18px; height: 18px; }
QPlainTextEdit {
    background: #0b0f16;
    border: 1px solid #273143;
    border-radius: 10px;
    color: #aeb9c9;
    padding: 8px;
    font-family: "Cascadia Mono";
    font-size: 12px;
}
"""
