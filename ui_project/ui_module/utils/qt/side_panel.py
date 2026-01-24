from PySide6.QtCore import Qt, QPropertyAnimation, Property
from PySide6.QtWidgets import QWidget, QVBoxLayout, QButtonGroup, QLabel, QPushButton
from ui_module.utils.world import World

class SidePanel(QWidget):

    def __init__(self, parent=None, collapsed_width=20, expanded_width=200, animation_duration=200):
        super().__init__(parent)

        self.collapsed_width = collapsed_width
        self.expanded_width = expanded_width

        # === Largeur initiale ===
        self._panelWidth = self.collapsed_width
        self.setFixedWidth(self._panelWidth)

        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.setAttribute(Qt.WA_Hover)

        # --- Layout principal ---
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # ------------------------------------------------------
        #  IMAGE visible quand le panneau est COLLAPSÉ
        # ------------------------------------------------------
        self.icon_label = QLabel()
        imported_image = World().collapsed_pixmap
        self.icon_label.setPixmap(imported_image)
        collapsed_height = int(collapsed_width * imported_image.height() / imported_image.width())
        self.icon_label.setScaledContents(True)
        self.icon_label.setFixedSize(collapsed_width, collapsed_height)

        self.setMouseTracking(True)
        self.icon_label.setMouseTracking(True)

        # ------------------------------------------------------
        #  CONTENU visible quand ouvert
        # ------------------------------------------------------
        self.buttons_container = QWidget()
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setContentsMargins(15, 20, 15, 20)
        self.buttons_layout.setSpacing(15)
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.buttons_container.setLayout(self.buttons_layout)

        # Groupe de boutons (facultatif mais pratique)
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # Ajout au layout principal
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.buttons_container)

        # Cache les boutons au début
        self.buttons_container.hide()

        # Animation
        self.animation = QPropertyAnimation(self, b"panelWidth")
        self.animation.setDuration(animation_duration)

        # Style des boutons
        self.buttons_container.setStyleSheet("""
        QPushButton {
            background-color: rgba(255, 255, 255, 20);
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            border: 1px solid rgba(255, 255, 255, 40);
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 40);
            border: 1px solid rgba(255, 255, 255, 70);
        }
        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 60);
        }
        QPushButton:checked {
            background-color: rgba(255, 255, 255, 80);
            border: 1px solid white;
        }
        """)

    # ======================================
    #   MÉTHODE GÉNÉRIQUE POUR AJOUTER UN BOUTON
    # ======================================
    def add_button(self, text: str, slot=None, checkable=True, checked=False):
        """
        Ajoute un bouton au panneau.
        - text : texte du bouton
        - slot : fonction appelée au clic
        - checkable : si True, fait partie du button_group
        - checked : sélection initiale si checkable
        Retourne l’objet QPushButton
        """

        btn = QPushButton(text)
        btn.setCheckable(checkable)

        if slot:
            btn.clicked.connect(slot)

        # Ajout au layout
        self.buttons_layout.insertWidget(self.buttons_layout.count() - 0, btn)

        # Ajout au groupe
        if checkable:
            self.button_group.addButton(btn)
            btn.setChecked(checked)

        return btn

    # ======================================
    #       PROPRIÉTÉ Qt animée
    # ======================================
    def getPanelWidth(self):
        return self._panelWidth

    def setPanelWidth(self, value):
        self._panelWidth = value
        self.setFixedWidth(value)
        self.update_visibility()

    panelWidth = Property(int, getPanelWidth, setPanelWidth)

    # ======================================
    #       VISIBILITÉ
    # ======================================
    def update_visibility(self):
        if self._panelWidth <= self.collapsed_width + 5:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
            self.icon_label.show()
            self.buttons_container.hide()
        else:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
            self.icon_label.hide()
            self.buttons_container.show()

    # ======================================
    #       ÉVÈNEMENTS SOURIS
    # ======================================
    def mouseMoveEvent(self, event):
        if self.icon_label.isVisible():
            pos = self.icon_label.mapFromParent(event.pos())
            pixmap = self.icon_label.pixmap()

            if pixmap:
                image = pixmap.toImage()
                if image.rect().contains(pos):
                    if image.pixelColor(pos).alpha() > 10:
                        self.animation.stop()
                        self.animation.setStartValue(self.getPanelWidth())
                        self.animation.setEndValue(self.expanded_width)
                        self.animation.start()
                        return

        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.getPanelWidth())
        self.animation.setEndValue(self.collapsed_width)
        self.animation.start()
        super().leaveEvent(event)
