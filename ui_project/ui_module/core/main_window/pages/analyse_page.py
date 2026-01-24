from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout

from ui_module.core.main_window.pages.analyse_page_widgets.players_settings_widget import PlayersSettingsWidget
from ui_module.utils.world import absolute_path_str
from ui_module.utils.qt.qt_utils import put_in_frame

class FixedRatioWidget(QWidget):
    """
    Widget qui garde un ratio hauteur = 2/3 largeur
    """
    def resizeEvent(self, event):
        # Récupère la largeur actuelle
        width = self.width()
        # Définit la hauteur = 2/3 largeur
        height = int(2 * width / 3)
        # Applique la hauteur
        self.setFixedHeight(height)
        super().resizeEvent(event)

class AnalysePage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("AnalysePage")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet(f"""
            QWidget#AnalysePage {{
                background-image: url("{absolute_path_str("ui_files/images/background_1.png")}");
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
            }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_widget = QWidget()
        main_layout.addWidget(main_widget)
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(20, 20, 20, 20)
        h_layout.setSpacing(20)

        label_1 = QLabel("Area 1")
        label_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_2 = QLabel("Area 2")
        label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_3 = QLabel("Area 3")
        label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_4 = QLabel("Area 4")
        label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        label_1.setFont(font)
        label_2.setFont(font)
        label_3.setFont(font)
        label_4.setFont(font)

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)

        top_widget = FixedRatioWidget()
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(put_in_frame(label_1))
        top_widget.setLayout(top_layout)

        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addWidget(put_in_frame(label_2))
        bottom_widget.setLayout(bottom_layout)

        left_layout.addWidget(top_widget)
        left_layout.addWidget(bottom_widget)

        left_layout.setStretch(0, 0)
        left_layout.setStretch(1, 1)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(20)

        right_layout.addWidget(put_in_frame(PlayersSettingsWidget()))

        left_widget.setLayout(left_layout)
        right_widget.setLayout(right_layout)

        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)

        h_layout.setStretch(0, 2)
        h_layout.setStretch(1, 1)
        main_widget.setLayout(h_layout)

        self.setLayout(main_layout)