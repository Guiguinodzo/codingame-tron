from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QVBoxLayout


def put_in_frame(widget, frame_radius = 2, frame_color = QColor(255, 255, 255, 180), background_color = QColor(0, 0, 0, 180)):
    frame = QFrame()
    frame.setObjectName("customFrame")

    fc = f"rgba({frame_color.red()}, {frame_color.green()}, {frame_color.blue()}, {frame_color.alpha()})"
    bc = f"rgba({background_color.red()}, {background_color.green()}, {background_color.blue()}, {background_color.alpha()})"

    frame.setStyleSheet(f"""
        QFrame#customFrame {{
            border: 2px solid {fc};
            border-radius: {frame_radius}px;
            background-color: {bc};
        }}
        
        QFrame#customFrame:disabled {{
            border: 2px solid rgba(120,120,120,120);
            border-radius: {frame_radius}px;
            background-color: rgba(120,120,120,120);
        }}
        """)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(frame_radius, frame_radius, frame_radius, frame_radius)
    layout.setSpacing(0)
    layout.addWidget(widget)

    return frame

def set_tron_button_style(button):
    button.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            border: 2px solid #00f6ff;
            border-radius: 2px;
            color: #7df9ff;
            font-size: 16px;
        }

        QPushButton:hover {
            background-color: rgba(0,246,255,60);
        }

        QPushButton:pressed {
            background-color: rgba(0,246,255,140);
        }

        QPushButton:disabled {
            background-color: transparent;
            border: 2px solid rgba(120,120,120,120);
            border-radius: 2px;
            color: rgba(120,120,120,120);
            font-size: 16px;
        }
        """)


def set_tron_spinbox_style(spinbox):
    spinbox.setStyleSheet("""
        QSpinBox {
            background-color: rgba(0,0,0,150);
            color: #7df9ff;
            border: 2px solid #00f6ff;
            border-radius: 6px;
            padding: 0px;
        }

        QSpinBox:disabled {
            background-color: rgba(40,40,40,150);
            color: rgba(150,150,150,180);
            border: 2px solid rgba(120,120,120,120);
        }

        QSpinBox::up-button, QSpinBox::down-button {
            background: transparent;
        }

        QSpinBox::up-button:disabled, 
        QSpinBox::down-button:disabled {
            background: transparent;
        }
        """)
