from PySide6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QApplication

from widgets.Other.DebugInfo import DebugInfo


class QuitWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(480, 480)

        self.debug_widget: DebugInfo | None = None
        self.debug_visible = False
        self.fade_anim: QPropertyAnimation | None = None

        # Exit button
        btn = QPushButton("✕")
        btn.setFixedSize(160, 160)
        btn.clicked.connect(QApplication.quit)

        btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                font-size: 64px;
                border: 2px solid white;
                border-radius: 80px;
            }
            QPushButton:pressed {
                background-color: #000000;
                color: white;
            }
        """)

        layout = QHBoxLayout(self)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

    # ---------- LONG PRESS HANDLER ----------

    def on_long_press(self):
        """Called externally. Toggles DebugInfo with fade animation."""
        if not self.debug_widget:
            self._create_debug_widget()

        if self.debug_visible:
            self._fade_out_debug()
        else:
            self._fade_in_debug()

        self.debug_visible = not self.debug_visible

    # ---------- INTERNAL HELPERS ----------

    def _create_debug_widget(self):
        self.debug_widget = DebugInfo(self)
        self.debug_widget.setGeometry(self.rect())
        self.debug_widget.hide()

        effect = QGraphicsOpacityEffect(self.debug_widget)
        effect.setOpacity(0.0)
        self.debug_widget.setGraphicsEffect(effect)

    def _fade_in_debug(self):
        self.debug_widget.show()
        self._animate_opacity(0.0, 1.0)

    def _fade_out_debug(self):
        self._animate_opacity(1.0, 0.0, hide_after=True)

    def _animate_opacity(self, start, end, hide_after=False):
        effect = self.debug_widget.graphicsEffect()

        if self.fade_anim:
            self.fade_anim.stop()

        self.fade_anim = QPropertyAnimation(effect, b"opacity", self)
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(start)
        self.fade_anim.setEndValue(end)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        if hide_after:
            self.fade_anim.finished.connect(self.debug_widget.hide)

        self.fade_anim.start()
