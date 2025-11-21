import sys
from PySide6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QRect, QEasingCurve, QEvent
from widgets.ClockWidget import ClockWidget
from widgets.WeatherStationWidget import WeatherStationWidget

class MainWindow(QWidget):
    def __init__(self, is_raspberry_pi=False):
        super().__init__()
        if is_raspberry_pi:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.showFullScreen()
        else:
            self.setFixedSize(480, 480)
        self.setStyleSheet("QWidget { background-color: black; }")

        self.pages = [
            ClockWidget(),
            WeatherStationWidget(),
        ]

        # lay them vertically
        for i, p in enumerate(self.pages):
            p.setParent(self)
            p.setGeometry(0, i * 480, 480, 480)
            p.show()

        self.current_index = 0

        self.drag_start = None
        self.dragging = False
        self.offset_y = 0

        self.animations = []

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.pos()
            self.dragging = True
            self.offset_y = 0

    def mouseMoveEvent(self, event):
        if not self.dragging:
            return

        dy = event.pos().y() - self.drag_start.y()

        # --- Rubber-band effect when out of bounds ---
        if (self.current_index == 0 and dy > 0) or \
           (self.current_index == len(self.pages)-1 and dy < 0):
            # Apply elastic resistance
            dy = dy / (abs(dy) / 150 + 1)

        self.offset_y = dy

        # Move all pages relative to drag
        for i, page in enumerate(self.pages):
            page_y = (i - self.current_index) * 480 + dy
            page.move(0, page_y)

    def mouseReleaseEvent(self, event):
        if not self.dragging:
            return

        self.dragging = False

        threshold = 120
        dy = self.offset_y

        # --- Out-of-bounds snap-back ---
        if (self.current_index == 0 and dy > 0) or \
           (self.current_index == len(self.pages)-1 and dy < 0):
            self.animate_to(self.current_index)  # snap to same page
            return

        # Normal switching
        if dy < -threshold and self.current_index < len(self.pages) - 1:
            self.animate_to(self.current_index + 1)
        elif dy > threshold and self.current_index > 0:
            self.animate_to(self.current_index - 1)
        else:
            self.animate_to(self.current_index)

    def animate_to(self, target_index):
        """Animate all pages so target_index becomes centered."""
        self.current_index = target_index

        for i, page in enumerate(self.pages):
            start_y = page.y()
            end_y = (i - target_index) * 480

            anim = QPropertyAnimation(page, b"pos")
            anim.setDuration(220)
            anim.setStartValue(QPoint(0, start_y))
            anim.setEndValue(QPoint(0, end_y))
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()

            self.animations.append(anim)