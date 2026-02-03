from PySide6.QtCore import Qt, QSize, QTimer, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QHBoxLayout, QPushButton, QLabel, QSpinBox

from ui_module.core.simulator.database import PlayersSettings
from ui_module.core.simulator.simulator_interface import InputPlayer
from ui_module.utils.qt.qt_utils import set_tron_button_style, set_tron_spinbox_style
from ui_module.utils.world import World


class GameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.grid_w = 30
        self.grid_h = 20

        self.players_paths: list[list[tuple[int, int]]] = [[], [], [], []]

        self.setMinimumSize(300, 200)

        self.players_settings = PlayersSettings()

        self.loading = False
        self.progress = 0
        self.banner_x = -1.0

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate_banner)

    # ---------------- API ----------------

    def set_state(self, players_paths: list[list[tuple[int, int]]]):
        """
        players_paths = [
            [(x,y), ...],  # player 0
            [(x,y), ...],  # player 1
            [(x,y), ...],  # player 2
            [(x,y), ...],  # player 3
        ]
        """
        self.players_paths = players_paths
        self.update()

    def clear(self):
        self.players_paths = [[], [], [], []]
        self.update()

    def start_loading(self):
        self.loading = True
        self.progress = 0
        self.banner_x = -self.width()
        self.anim_timer.start(16)
        self.update()

    def set_progress(self, value: float):
        self.progress = max(0, min(100, int(value)))
        self.update()

    def stop_loading(self):
        self.loading = False
        self.anim_timer.stop()
        self.update()

    # ---------------- DRAW ----------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        cell_w = w / self.grid_w
        cell_h = h / self.grid_h

        # ---- background ----
        painter.fillRect(self.rect(), QColor(0, 0, 0, 220))

        # ---- grid ----
        grid_pen = QPen(QColor(0, 246, 255, 60))
        painter.setPen(grid_pen)

        for x in range(self.grid_w + 1):
            painter.drawLine(int(x * cell_w), 0, int(x * cell_w), h)

        for y in range(self.grid_h + 1):
            painter.drawLine(0, int(y * cell_h), w, int(y * cell_h))

        # ---- players ----
        for player_index, path in enumerate(self.players_paths):
            if not path:
                continue

            color = self.players_settings.get_color(player_index)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))

            for x, y in path:
                rect = QRectF(
                    x * cell_w,
                    y * cell_h,
                    cell_w,
                    cell_h
                )
                painter.drawRect(rect)

        if self.loading:
            self.draw_loading_overlay(painter)

        painter.end()

    def draw_loading_overlay(self, painter: QPainter):
        w = self.width()
        h = self.height()

        banner_h = h * 0.22
        y = (h - banner_h) / 2

        # glow background
        grad = QLinearGradient(0, y, w, y + banner_h)
        grad.setColorAt(0.0, QColor(0, 255, 255, 30))
        grad.setColorAt(0.5, QColor(0, 255, 255, 200))
        grad.setColorAt(1.0, QColor(0, 255, 255, 30))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))

        rect = QRectF(self.banner_x, y, w, banner_h)
        painter.drawRoundedRect(rect, 12, 12)

        # text
        painter.setPen(QColor(0, 0, 0))
        font = painter.font()
        font.setPointSize(int(banner_h * 0.25))
        font.setBold(True)
        painter.setFont(font)

        text = f"SIMULATION — {self.progress}%"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    # ---------------- ANIMATION ----------------

    def animate_banner(self):
        speed = self.width() * 0.08

        if self.banner_x < 0:
            self.banner_x += speed
            if self.banner_x > 0:
                self.banner_x = 0

        self.update()

    # ---------------- UI ----------------

    def resizeEvent(self, event):
        # Récupère la largeur actuelle
        width = self.width()
        # Définit la hauteur = 2/3 largeur
        height = int(2 * width / 3)
        # Applique la hauteur
        self.setFixedHeight(height)
        super().resizeEvent(event)


class BoardGameWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.world = World()

        self.game_computed = False
        self.current_step = int(0)

        self.main_layout = QVBoxLayout()

        self.game_widget = GameWidget()
        self.main_layout.addWidget(self.game_widget)

        self.max_steps = 100

        # ---------------- SLIDER ----------------
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, self.max_steps)
        self.timeline_slider.setValue(0)

        self.timeline_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(0,0,0,150);
                border: 1px solid #00f6ff;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                width: 14px;
                margin: -6px 0;
                background: #00f6ff;
                border-radius: 7px;
            }
        """)

        self.main_layout.addWidget(self.timeline_slider)

        # ---------------- CONTROLS ----------------
        controls_layout = QHBoxLayout()
        icon_size = 20

        self.prev_btn = QPushButton("")
        self.prev_btn.setIcon(self.world.fast_backward_icon)
        self.prev_btn.setIconSize(QSize(icon_size, icon_size))
        self.prev_btn.setFixedSize(icon_size + 10, icon_size + 10)
        set_tron_button_style(self.prev_btn)
        self.play_btn = QPushButton("")
        self.play_btn.setIcon(self.world.play_icon)
        self.play_btn.setIconSize(QSize(icon_size, icon_size))
        self.play_btn.setFixedSize(icon_size + 10, icon_size + 10)
        set_tron_button_style(self.play_btn)
        self.next_btn = QPushButton("")
        self.next_btn.setIcon(self.world.fast_forward_icon)
        self.next_btn.setIconSize(QSize(icon_size, icon_size))
        self.next_btn.setFixedSize(icon_size + 10, icon_size + 10)
        set_tron_button_style(self.next_btn)

        self.step_label = QLabel("Step:")
        self.step_label.setStyleSheet("color:#7df9ff; font-size:14px;")

        self.step_spin = QSpinBox()
        self.step_spin.setRange(0, self.max_steps)
        set_tron_spinbox_style(self.step_spin)

        self.speed_label = QLabel("speed:")
        self.speed_label.setStyleSheet("color:#7df9ff; font-size:14px;")

        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 100)
        self.speed_spin.setValue(self.world.ui_settings.get_board_game_speed())
        set_tron_spinbox_style(self.speed_spin)

        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.step_label)
        controls_layout.addWidget(self.step_spin)
        controls_layout.addStretch()
        controls_layout.addWidget(self.speed_label)
        controls_layout.addWidget(self.speed_spin)

        self.main_layout.addLayout(controls_layout)


        # --- PLAY TIMER ---
        self.is_playing = False
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._play_step)


        # ---------------- SIGNALS (placeholder) ----------------
        self.timeline_slider.valueChanged.connect(self.on_slider_changed)
        self.step_spin.valueChanged.connect(self.on_spin_changed)
        self.prev_btn.clicked.connect(self.on_prev)
        self.next_btn.clicked.connect(self.on_next)
        self.play_btn.clicked.connect(self.on_play_pause)
        self.speed_spin.valueChanged.connect(self.on_speed_changed)

        self.setLayout(self.main_layout)

        self.stop_signals = True
        self.set_value(0)
        self.stop_signals = False

        self._enable_widgets()

    # ---------------- API ----------------

    def set_max_steps(self, steps: int):
        self.max_steps = steps
        self.timeline_slider.setRange(0, steps - 1)
        self.step_spin.setRange(0, steps - 1)

    # ---------------- SLOTS ----------------

    def _play_step(self):
        v = self.timeline_slider.value() + 1

        if v > self.timeline_slider.maximum():
            self.stop_play()
            return

        self.stop_signals = True
        self.set_value(v)
        self.stop_signals = False


    def on_slider_changed(self, value: int):
        if not self.stop_signals:
            self.stop_play()
            self.stop_signals = True
            self.set_value(value)
            self.stop_signals = False

    def on_spin_changed(self, value: int):
        if not self.stop_signals:
            self.stop_play()
            self.stop_signals = True
            self.set_value(value)
            self.stop_signals = False

    def on_prev(self):
        if not self.stop_signals:
            v = max(0, self.timeline_slider.value() - 1)
            self.stop_play()
            self.stop_signals = True
            self.set_value(v)
            self.stop_signals = False

    def on_next(self):
        if not self.stop_signals:
            v = min(self.timeline_slider.maximum(), self.timeline_slider.value() + 1)
            self.stop_play()
            self.stop_signals = True
            self.set_value(v)
            self.stop_signals = False

    def on_play_pause(self):
        if not self.is_playing:
            self.start_play()
        else:
            self.stop_play()

    def on_speed_changed(self, value: int):
        self.play_timer.setInterval(int(1000 / self.speed_spin.value()))
        self.world.ui_settings.set_board_game_speed(self.speed_spin.value())

    def start_play(self):
        self.is_playing = True
        self.play_timer.setInterval(int(1000 / self.speed_spin.value()))
        self.play_timer.start()
        self.play_btn.setIcon(self.world.pause_icon)

    def stop_play(self):
        self.is_playing = False
        self.play_timer.stop()
        self.play_btn.setIcon(self.world.play_icon)

    def set_value(self, value):
        self.current_step = value
        self.timeline_slider.setValue(value)
        self.step_spin.setValue(value)
        self._enable_widgets()
        if self.game_computed:
            board = self.world.simulator.get_board_at(value)
            positions = []
            for index in range(self.world.player_settings.PLAYER_COUNT):
                found = False
                for player in board.players:
                    if player.id == index:
                        positions.append(player.trail)
                        found = True
                        continue
                if not found:
                    positions.append([])
            self.game_widget.set_state(positions)

    def _enable_widgets(self):
        self.speed_spin.setEnabled(self.game_computed)
        self.speed_label.setEnabled(self.game_computed)
        self.step_spin.setEnabled(self.game_computed)
        self.step_label.setEnabled(self.game_computed)
        self.timeline_slider.setEnabled(self.game_computed)
        self.next_btn.setEnabled(self.game_computed)
        self.prev_btn.setEnabled(self.game_computed and self.current_step > 0)
        self.play_btn.setEnabled(self.game_computed and self.current_step < self.max_steps)

    def simulator_started(self):
        self.game_computed = False
        self.world.simulator.advancement.connect(self.simulator_progress)
        self.world.simulator.finished.connect(self.simulator_finished)
        self.game_widget.start_loading()
        self._enable_widgets()

        input_players = []
        for i in range(self.world.player_settings.PLAYER_COUNT):
            if self.world.player_settings.get_enable(i):
                input_players.append(
                    InputPlayer(
                        id = i,
                        ai_path = self.world.player_settings.get_ai_path(i),
                        random_pos = self.world.player_settings.get_random_pos(i),
                        starting_pos = None if self.world.player_settings.get_random_pos(i) else self.world.player_settings.get_position(i)
                    )
                )
        self.world.simulator.start_simulation(input_players)

    def simulator_progress(self, percent):
        self.game_widget.set_progress(percent)

    def simulator_finished(self):
        if not self.game_computed:
            self.game_computed = True
            self.set_max_steps(self.world.simulator.get_total_step_number())
            self.game_widget.stop_loading()
            self._enable_widgets()
            self.set_value(0)