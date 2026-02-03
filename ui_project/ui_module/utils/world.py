import sys
from pathlib import Path

from PySide6.QtGui import QPixmap, QIcon

from ui_module.core.simulator.database import PlayersSettings, UISettings
from ui_module.core.simulator.simulator_impl import Simulator


def absolute_path(relative_path: str) -> Path:
    """Retourne un chemin utilisable, en mode dev ET en mode PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        # En exécutable PyInstaller
        return Path(sys._MEIPASS) / relative_path
    else:
        # En mode développement (dans ton IDE)
        return Path(__file__).resolve().parent.parent.parent / relative_path

def absolute_path_str(relative_path: str) -> str:
    return str(absolute_path(relative_path)).replace("\\", "/")

class World:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Empêche plusieurs initialisations
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True
        self._load_resources()
        self.player_settings = PlayersSettings()
        self.ui_settings = UISettings()
        self.simulator = Simulator()

    def _load_resources(self):
        self.collapsed_pixmap = QPixmap(absolute_path_str("ui_files/images/collapsed.png"))
        self.save_icon = QIcon(absolute_path_str("ui_files/images/save_icon.png"))
        self.load_icon = QIcon(absolute_path_str("ui_files/images/load_icon.png"))
        self.size_down_icon = QIcon(absolute_path_str("ui_files/images/size_down_icon.png"))
        self.size_up_icon = QIcon(absolute_path_str("ui_files/images/size_up_icon.png"))
        self.play_icon = QIcon(absolute_path_str("ui_files/images/play_icon.png"))
        self.pause_icon = QIcon(absolute_path_str("ui_files/images/pause_icon.png"))
        self.fast_forward_icon = QIcon(absolute_path_str("ui_files/images/fast_forward_icon.png"))
        self.fast_backward_icon = QIcon(absolute_path_str("ui_files/images/fast_backward_icon.png"))