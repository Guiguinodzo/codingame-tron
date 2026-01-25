from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QHBoxLayout, QPushButton, QLabel, QSpinBox

from ui_module.utils.qt.qt_utils import set_tron_button_style, set_tron_spinbox_style
from ui_module.utils.world import World


class GameWidget(QWidget):
    def __init__(self):
        super().__init__()


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

        self.main_layout = QVBoxLayout()

        self.game_widget = GameWidget()
        self.main_layout.addWidget(self.game_widget)

        # ---------------- SLIDER ----------------
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 100)
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

        self.step_label = QLabel("Coup:")
        self.step_label.setStyleSheet("color:#7df9ff; font-size:14px;")

        self.step_spin = QSpinBox()
        self.step_spin.setRange(0, 100)

        set_tron_spinbox_style(self.step_spin)

        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.step_label)
        controls_layout.addWidget(self.step_spin)
        controls_layout.addStretch()

        self.main_layout.addLayout(controls_layout)


        # --- PLAY TIMER ---
        self.is_playing = False
        self.play_timer = QTimer(self)
        self.play_timer.setInterval(500)  # 0.5 sec
        self.play_timer.timeout.connect(self._play_step)


        # ---------------- SIGNALS (placeholder) ----------------
        self.timeline_slider.valueChanged.connect(self.on_slider_changed)
        self.step_spin.valueChanged.connect(self.on_spin_changed)
        self.prev_btn.clicked.connect(self.on_prev)
        self.next_btn.clicked.connect(self.on_next)
        self.play_btn.clicked.connect(self.on_play_pause)

        self.setLayout(self.main_layout)

    # ---------------- API ----------------

    def set_max_steps(self, steps: int):
        self.timeline_slider.setRange(0, steps)
        self.step_spin.setRange(0, steps)

    # ---------------- SLOTS ----------------

    def _play_step(self):
        v = self.timeline_slider.value() + 1

        if v > self.timeline_slider.maximum():
            self.stop_play()
            return

        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(v)
        self.timeline_slider.blockSignals(False)


    def on_slider_changed(self, value: int):
        self.stop_play()
        self.step_spin.blockSignals(True)
        self.step_spin.setValue(value)
        self.step_spin.blockSignals(False)

    def on_spin_changed(self, value: int):
        self.stop_play()
        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(value)
        self.timeline_slider.blockSignals(False)

    def on_prev(self):
        v = max(0, self.timeline_slider.value() - 1)
        self.stop_play()
        self.timeline_slider.setValue(v)

    def on_next(self):
        v = min(self.timeline_slider.maximum(), self.timeline_slider.value() + 1)
        self.stop_play()
        self.timeline_slider.setValue(v)

    def on_play_pause(self):
        if not self.is_playing:
            self.start_play()
        else:
            self.stop_play()

    def start_play(self):
        self.is_playing = True
        self.play_timer.start()
        self.play_btn.setIcon(self.world.pause_icon)

    def stop_play(self):
        self.is_playing = False
        self.play_timer.stop()
        self.play_btn.setIcon(self.world.play_icon)
