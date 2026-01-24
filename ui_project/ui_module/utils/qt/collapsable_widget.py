from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QByteArray
from PySide6.QtWidgets import QWidget


class CollapsableWidget(QWidget):
    def __init__(self, content_layout, start_collapsed = False, control_button = None):
        super().__init__()

        self.setLayout(content_layout)
        self.setMaximumHeight(16777215)
        self.open_height = self.sizeHint().height()

        self.is_collapsed = start_collapsed

        # Animation
        self.animation = QPropertyAnimation(self, QByteArray(b"maximumHeight"))
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        if control_button:
            control_button.clicked.connect(self.toggle_animation)

    def toggle_animation(self):
        if self.is_collapsed:
            # Déplier
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.open_height)
        else:
            # Réduire
            self.animation.setStartValue(self.height())
            self.animation.setEndValue(0)

        self.animation.start()
        self.is_collapsed = not self.is_collapsed