from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget

from ui_module.core.main_window.pages.analyse_page import AnalysePage
from ui_module.core.main_window.pages.arena_page import ArenaPage
from ui_module.utils.qt.side_panel import SidePanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tron AI")
        self.resize(1200, 800)

        # Widget central
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # --- STACKED WIDGET ---
        self.stacked = QStackedWidget()
        layout.addWidget(self.stacked)

        self.analyse_page = AnalysePage()
        self.arena_page = ArenaPage()

        self.stacked.addWidget(self.analyse_page)
        self.stacked.addWidget(self.arena_page)

        self.side_panel = SidePanel(self)
        self.side_panel.setParent(self)

        # Positionner à gauche
        self.side_panel.move(0, 0)

        # S’assurer qu’il se superpose
        self.side_panel.raise_()

        # Connexions des boutons du panel
        self.side_panel.add_button("Analyse", slot=lambda: self.show_page(self.analyse_page), checked=True)
        self.side_panel.add_button("Arena", slot=lambda: self.show_page(self.arena_page))

    def show_page(self, page):
        self.stacked.setCurrentWidget(page)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "side_panel"):
            self.side_panel.setFixedHeight(self.height())