import os

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QCheckBox, QSpinBox, QColorDialog, \
    QFileDialog

from dataclasses import dataclass

from ui_module.utils.qt.collapsable_widget import CollapsableWidget
from ui_module.utils.qt.qt_utils import set_tron_button_style, put_in_frame, set_tron_spinbox_style
from ui_module.utils.world import World

@dataclass
class PlayerUI:
    widget: QWidget
    enable: QCheckBox
    random_pos: QCheckBox
    choose: QLabel
    color: QPushButton
    x: QSpinBox
    y: QSpinBox
    load: QPushButton
    path: QLabel


class PlayersSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.world = World()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.top_part_layout = QVBoxLayout()
        self.top_part_layout.setContentsMargins(0, 0, 0, 0)
        self.top_part_layout.setSpacing(0)
        self.top_widget = QWidget()
        self.top_layout = QHBoxLayout()
        self.load_button = QPushButton("")
        self.load_button.setIcon(self.world.load_icon)
        self.load_button.setIconSize(QSize(32, 32))
        self.load_button.setFixedSize(48, 48)
        set_tron_button_style(self.load_button)
        self.load_button.clicked.connect(self._load_settings)
        self.load_button.setToolTip("Load player settings.")
        self.save_button = QPushButton("")
        self.save_button.setIcon(self.world.save_icon)
        self.save_button.setIconSize(QSize(32, 32))
        self.save_button.setFixedSize(48, 48)
        set_tron_button_style(self.save_button)
        self.save_button.clicked.connect(self._save_settings)
        self.save_button.setToolTip("Export player settings.")
        self.open = True
        self.open_button = QPushButton("")
        self.open_button.setIcon(self.world.size_down_icon)
        self.open_button.setIconSize(QSize(32, 32))
        self.open_button.setFixedSize(48, 48)
        set_tron_button_style(self.open_button)
        self.open_button.clicked.connect(self.open_close)
        self.open_button.setToolTip("Hide player settings.")
        self.top_layout.addWidget(self.load_button)
        self.top_layout.addWidget(self.save_button)
        self.top_layout.addWidget(self.open_button)
        self.top_widget.setLayout(self.top_layout)
        self.top_part_layout.addWidget(self.top_widget)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)
        self.players: list[PlayerUI] = []

        colors = [
            QColor(255, 80, 80),
            QColor(80, 255, 80),
            QColor(80, 80, 255),
            QColor(255, 255, 80),
        ]

        for i in range(self.world.player_settings.PLAYER_COUNT):
            player = self.create_player_widget(i, colors[i])
            self.players.append(player)
            self.content_layout.addWidget(put_in_frame(player.widget))

        self.collapsable_widget = CollapsableWidget(self.content_layout, False, self.open_button)
        self.top_part_layout.addWidget(self.collapsable_widget)

        self.layout.addLayout(self.top_part_layout)

        self.start_layout = QHBoxLayout()
        self.start_button = QPushButton(" Run Simulation ")
        self.start_layout.addStretch()
        set_tron_button_style(self.start_button)
        self.start_layout.addWidget(self.start_button)
        self.start_layout.addStretch()

        self.layout.addLayout(self.start_layout)

        self.layout.addStretch()

        self.setLayout(self.layout)
        self._load_database()
        self.start_button.clicked.connect(self._start_simulation)

    def create_player_widget(self, index: int, default_color: QColor) -> PlayerUI:
        widget = QWidget()
        v_layout = QVBoxLayout(widget)
        v_layout.setContentsMargins(0, 0, 0, 0)

        # -------- Row 0 --------
        h0 = QHBoxLayout()
        h0.setContentsMargins(0, 0, 0, 0)

        enable = QCheckBox(f"Activate Player {index}")
        enable.setStyleSheet("""
            QCheckBox {
                color: #7df9ff;
                font-size: 16px;
                spacing: 8px;
            }
        """)

        color_picker = QPushButton()
        color_picker.setFixedSize(QSize(20, 20))
        color_picker.setStyleSheet(f"""
            QPushButton {{
                background-color: {default_color.name()};
            }}
            
            QPushButton:disabled {{
                background-color: rgba(120,120,120,120);
            }}
            """)

        h0.addWidget(enable)
        h0.addStretch()

        color_label = QLabel("Choose color:")
        color_label.setStyleSheet("""
            QLabel {
                color: #7df9ff;
                font-size: 16px;
            }
            
            QLabel:disabled {
                color: rgba(120,120,120,120);
                font-size: 16px;
            }
        """)
        h0.addWidget(color_label)
        h0.addWidget(color_picker)
        h0.addStretch()

        v_layout.addLayout(h0)

        # -------- Row 1 --------
        h1 = QHBoxLayout()
        h1.setContentsMargins(0, 0, 0, 0)

        random_position = QCheckBox(f"Random position")
        random_position.setStyleSheet("""
            QCheckBox {
                color: #7df9ff;
                font-size: 16px;
                spacing: 8px;
            }
            
            QCheckBox:disabled {
                color: rgba(120,120,120,120);
                font-size: 16px;
                spacing: 8px;
            }
        """)

        x_spin = QSpinBox()
        y_spin = QSpinBox()
        x_spin.setRange(0, 29)
        y_spin.setRange(0, 19)
        x_spin.setPrefix("X: ")
        y_spin.setPrefix("Y: ")

        set_tron_spinbox_style(x_spin)
        set_tron_spinbox_style(y_spin)
        h1.addWidget(random_position)
        h1.addWidget(x_spin)
        h1.addWidget(y_spin)
        h1.addStretch()

        v_layout.addLayout(h1)

        # -------- Row 2 --------
        h2 = QHBoxLayout()
        h2.setContentsMargins(0, 0, 0, 0)

        load_btn = QPushButton()
        load_btn.setIcon(self.world.load_icon)
        load_btn.setIconSize(QSize(16, 16))
        load_btn.setFixedSize(24, 24)
        set_tron_button_style(load_btn)

        path_label = QLabel("AI not loaded.")
        path_label.setStyleSheet("""
            QLabel {
                color: #7df9ff;
                font-size: 16px;
            }
            
            QLabel:disabled {
                color: rgba(120,120,120,120);
                font-size: 16px;
            }
        """)

        h2.addWidget(load_btn)
        h2.addWidget(path_label)
        h2.addStretch()

        v_layout.addLayout(h2)

        # -------- Signals
        enable.toggled.connect(lambda v, i=index: self.on_player_enable(i, v))
        random_position.toggled.connect(lambda v, i=index: self.on_random_pos(i, v))
        color_picker.clicked.connect(lambda _, i=index: self.on_color_pick(i))
        x_spin.valueChanged.connect(lambda _, i=index: self.on_player_position_changed(i))
        y_spin.valueChanged.connect(lambda _, i=index: self.on_player_position_changed(i))
        load_btn.clicked.connect(lambda _, i=index: self.on_player_load_clicked(i))

        return PlayerUI(
            widget=widget,
            enable=enable,
            random_pos=random_position,
            choose=color_label,
            color=color_picker,
            x=x_spin,
            y=y_spin,
            load=load_btn,
            path=path_label,
        )

    def _enable_widgets(self):
        non_loaded_enabled_ai = False
        enabled_load_ai = [False] * 4
        for i in range(self.world.player_settings.PLAYER_COUNT):
            self.players[i].random_pos.setEnabled(self.players[i].enable.isChecked())
            self.players[i].choose.setEnabled(self.players[i].enable.isChecked())
            self.players[i].color.setEnabled(self.players[i].enable.isChecked())
            self.players[i].x.setEnabled(self.players[i].enable.isChecked() and not self.players[i].random_pos.isChecked())
            self.players[i].y.setEnabled(self.players[i].enable.isChecked() and not self.players[i].random_pos.isChecked())
            self.players[i].load.setEnabled(self.players[i].enable.isChecked())
            self.players[i].path.setEnabled(self.players[i].enable.isChecked())
            if self.players[i].enable.isChecked():
                if self.world.player_settings.get_ai_path(i):
                    enabled_load_ai[i] = True
                else:
                    non_loaded_enabled_ai = True

        if non_loaded_enabled_ai:
            self.start_button.setEnabled(False)
            self.start_button.setToolTip("You need to load all enabled AI.")
        else:
            if enabled_load_ai.count(True) > 1:
                non_random_starting_pos = []
                for i in range(self.world.player_settings.PLAYER_COUNT):
                    if enabled_load_ai[i] and not self.players[i].random_pos.isChecked():
                        non_random_starting_pos.append((self.players[i].x.value(), self.players[i].y.value()))
                if len(non_random_starting_pos) > 0 and len(non_random_starting_pos) != len(set(non_random_starting_pos)):
                    self.start_button.setEnabled(False)
                    self.start_button.setToolTip("You cannot have two identical starting positions.")
                else:
                    self.start_button.setEnabled(True)
                    self.start_button.setToolTip("")
            else:
                self.start_button.setEnabled(False)
                self.start_button.setToolTip("You need to have at least 2 enabled and loaded AI.")



    def _load_database(self):
        for i in range(self.world.player_settings.PLAYER_COUNT):
            self.players[i].enable.setChecked(self.world.player_settings.get_enable(i))
            self.players[i].color.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.world.player_settings.get_color(i).name()};
                }}

                QPushButton:disabled {{
                    background-color: rgba(120,120,120,120);
                }}
                """)
            self.players[i].random_pos.setChecked(self.world.player_settings.get_random_pos(i))
            x, y = self.world.player_settings.get_position(i)
            self.players[i].x.setValue(x)
            self.players[i].y.setValue(y)
            path = self.world.player_settings.get_ai_path(i)
            if path:
                if len(path) > 40:
                    self.players[i].path = "..." + self.world.player_settings.get_ai_path(i)[-37:]
                self.players[i].path.setText(path)
        self._enable_widgets()

    def open_close(self):
        if self.open:
            self.open_button.setIcon(self.world.size_up_icon)
            self.open_button.setToolTip("Show player settings.")
        else:
            self.open_button.setIcon(self.world.size_down_icon)
            self.open_button.setToolTip("Hide player settings.")
        self.open_button.setIconSize(QSize(32, 32))
        self.open = not self.open

    def _load_settings(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load player settings",
            self.world.ui_settings.get_json_last_path(),
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        self.world.player_settings.import_json(path)
        self.world.ui_settings.set_json_last_path(os.path.dirname(path))
        self._load_database()

    def _save_settings(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export player settings",
            self.world.ui_settings.get_json_last_path(),
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        self.world.player_settings.export_json(path)

    def on_player_enable(self, player_index, checked):
        self.world.player_settings.set_enable(player_index, checked)
        self._enable_widgets()

    def on_random_pos(self, player_index, checked):
        self.world.player_settings.set_random_pos(player_index, checked)
        self._enable_widgets()

    def on_color_pick(self, player_index):
        color = QColorDialog.getColor()
        if color.isValid():
            self.players[player_index].color.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                }}

                QPushButton:disabled {{
                    background-color: rgba(120,120,120,120);
                }}
                """)
            self.world.player_settings.set_color(player_index, color)
        self._enable_widgets()

    def on_player_position_changed(self, player_index):
        self.world.player_settings.set_position(player_index, self.players[player_index].x.value(), self.players[player_index].y.value())
        x, y = self.world.player_settings.get_position(player_index)
        self._enable_widgets()

    def on_player_load_clicked(self, player_index):
        (filename, _) = QFileDialog.getOpenFileName(self, "Open experiment configuration", self.world.ui_settings.get_ai_last_path(), "(*.py)")
        if filename:
            self.world.player_settings.set_ai_path(player_index, filename)
            self.world.ui_settings.set_ai_last_path(os.path.dirname(filename))
            if len(filename) > 30:
                self.players[player_index].path.setText("..." + filename[-27:])
            self.players[player_index].path.setText(filename)
            self._enable_widgets()

    def _start_simulation(self):
        print("start simulation")