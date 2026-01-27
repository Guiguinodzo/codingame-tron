import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QToolTip
from ui_module.core.main_window.main_window import MainWindow

def open_main_window():
    app = QApplication(sys.argv)

    QToolTip.setFont(QFont("Segoe UI", 10))

    app.setStyleSheet("""
    QToolTip {
        color: #7df9ff;
        background-color: rgba(0, 0, 0, 230);
        border: 1px solid #00f6ff;
        border-radius: 6px;
        padding: 2px 4px;
        font-size: 12px;
    }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    open_main_window()
