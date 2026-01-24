import sys
from PySide6.QtWidgets import QApplication
from core.main_window.main_window import MainWindow

def open_main_window():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    open_main_window()
