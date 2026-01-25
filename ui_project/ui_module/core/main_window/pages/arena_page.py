from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from ui_module.utils.world import absolute_path_str

class ArenaPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"""
            background-image: url("{absolute_path_str("ui_files/images/background_0.png")}");
            background-repeat: no-repeat;
            background-position: center;
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Arena page : Work in progress")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        label.setFont(font)

        layout.addWidget(label)
        self.setLayout(layout)