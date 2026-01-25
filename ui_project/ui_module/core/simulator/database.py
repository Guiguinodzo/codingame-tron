import json
import os.path

from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor


class UISettings:

    def __init__(self):
        self.settings = QSettings("CondingGame", "Tron")

        self._json_last_path = ""
        self._ai_last_path = ""
        self._board_game_speed = 1

        self._load()

    def _load(self):
        self._json_last_path = self.settings.value("ui/json_last_path", "", type=str)
        self._ai_last_path = self.settings.value("ui/ai_last_path", "", type=str)
        self._board_game_speed = self.settings.value("ui/board_game_speed", "", type=int)

    def get_json_last_path(self):
        if len(self._json_last_path) > 0 and os.path.exists(self._json_last_path):
            return self._json_last_path
        return ""

    def set_json_last_path(self, path: str):
        if path and len(path) > 0:
            self._json_last_path = path
            self.settings.setValue("ui/json_last_path", path)
            self.settings.sync()

    def get_ai_last_path(self):
        if len(self._ai_last_path) > 0 and os.path.exists(self._ai_last_path):
            return self._ai_last_path
        return ""

    def set_ai_last_path(self, path: str):
        if path and len(path) > 0:
            self._ai_last_path = path
            self.settings.setValue("ui/ai_last_path", path)
            self.settings.sync()

    def get_board_game_speed(self):
        return self._board_game_speed

    def set_board_game_speed(self, speed):
        self._board_game_speed = speed
        self.settings.setValue("ui/board_game_speed", speed)
        self.settings.sync()


class PlayerData:
    def __init__(self, color):
        self.enable = True
        self.color = color
        self.random_pos = True
        self.pos_x = 0
        self.pos_y = 0
        self.ai_path = None


class PlayersSettings:
    PLAYER_COUNT = 4

    def __init__(self):
        self.settings = QSettings("CondingGame", "Tron")

        colors = [
            QColor(255, 80, 80),
            QColor(80, 255, 80),
            QColor(80, 80, 255),
            QColor(255, 255, 80),
        ]
        self._players: list[PlayerData] = [PlayerData(colors[i]) for i in range(self.PLAYER_COUNT)]
        self._load()

    # ---------- LOAD / SAVE ----------

    def export_json(self, file_path: str):
        data = []

        for p in self._players:
            data.append({
                "enable": p.enable,
                "color": p.color.name(),
                "random_pos": p.random_pos,
                "pos_x": p.pos_x,
                "pos_y": p.pos_y,
                "ai_path": p.ai_path,
            })

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def import_json(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for i, pdata in enumerate(data):
            if i >= self.PLAYER_COUNT:
                break

            p = self._players[i]

            p.enable = pdata.get("enable", False)
            p.color = QColor(pdata.get("color", "#ffffff"))
            p.random_pos = pdata.get("random_pos", False)
            p.pos_x = pdata.get("pos_x", 0)
            p.pos_y = pdata.get("pos_y", 0)
            p.ai_path = pdata.get("ai_path", None)

            # sync QSettings
            self.set_enable(i, p.enable)
            self.set_color(i, p.color)
            self.set_random_pos(i, p.random_pos)
            self.set_position(i, p.pos_x, p.pos_y)
            self.set_ai_path(i, p.ai_path)

    def _load(self):
        for i in range(self.PLAYER_COUNT):
            p = self._players[i]
            self.settings.beginGroup(f"player_{i}")

            p.enable = self.settings.value("enable", False, type=bool)
            p.random_pos = self.settings.value("random_pos", False, type=bool)
            p.pos_x = self.settings.value("pos_x", 0, type=int)
            p.pos_y = self.settings.value("pos_y", 0, type=int)
            p.ai_path = self.settings.value("ai_path", None, type=str)

            color_str = self.settings.value("color", "#ffffff")
            p.color = QColor(color_str)

            self.settings.endGroup()

    def save(self):
        for i in range(self.PLAYER_COUNT):
            p = self._players[i]
            self.settings.beginGroup(f"player_{i}")

            self.settings.setValue("enable", p.enable)
            self.settings.setValue("random_pos", p.random_pos)
            self.settings.setValue("pos_x", p.pos_x)
            self.settings.setValue("pos_y", p.pos_y)
            self.settings.setValue("ai_path", p.ai_path)
            self.settings.setValue("color", p.color.name())

            self.settings.endGroup()

        self.settings.sync()

    # ---------- GETTERS / SETTERS ----------

    def set_enable(self, index: int, value: bool):
        self._players[index].enable = value
        self.settings.setValue(f"player_{index}/enable", value)

    def get_enable(self, index: int):
        return self._players[index].enable

    def set_color(self, index: int, color: QColor):
        self._players[index].color = color
        self.settings.setValue(f"player_{index}/color", color.name())

    def get_color(self, index: int):
        return self._players[index].color

    def set_random_pos(self, index: int, value: bool):
        self._players[index].random_pos = value
        self.settings.setValue(f"player_{index}/random_pos", value)

    def get_random_pos(self, index: int):
        return self._players[index].random_pos

    def set_position(self, index: int, x: int, y: int):
        p = self._players[index]
        p.pos_x = x
        p.pos_y = y
        self.settings.setValue(f"player_{index}/pos_x", x)
        self.settings.setValue(f"player_{index}/pos_y", y)

    def get_position(self, index: int):
        return self._players[index].pos_x, self._players[index].pos_y

    def set_ai_path(self, index: int, path: str):
        self._players[index].ai_path = path
        self.settings.setValue(f"player_{index}/ai_path", path)

    def get_ai_path(self, index: int):
        return self._players[index].ai_path