import sys
from PySide6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QRect, QEasingCurve, QEvent

from widgets.ArtificialHorizonWidget import ArtificialHorizonWidget
from widgets.ClockWidget import ClockWidget
from widgets.WeatherStationWidget import WeatherStationWidget
from widgets.MapWidget import MapWidget
from widgets.QuitWidget import QuitWidget

class MainWindow(QWidget):
    def __init__(self, is_raspberry_pi=False):
        super().__init__()

        if is_raspberry_pi:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.showFullScreen()
        else:
            self.setFixedSize(480, 480)
        self.setStyleSheet("QWidget { background-color: black; }")
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)  # Enable multitouch

        # Create all pages as children stacked vertically
        self.pages = [
            QuitWidget(),
            ClockWidget(),
            WeatherStationWidget(is_raspberry_pi),
            ArtificialHorizonWidget(is_raspberry_pi),
            MapWidget(),
        ]

        for i, page in enumerate(self.pages):
            page.setParent(self)
            page.setGeometry(0, i * 480, 480, 480)
            page.show()

        self.current_index = 0

        # Drag/touch state
        self.drag_start = None
        self.dragging = False
        self.offset_y = 0
        self.primary_touch_id = None  # The ID of the active finger
        self.animations = []

    # ───────────────────────────────────────────────
    # TOUCH EVENTS
    # ───────────────────────────────────────────────
    def event(self, event):
        # Let children (buttons, sliders, labels) receive touch first
        if event.type() in (QEvent.TouchBegin, QEvent.TouchUpdate, QEvent.TouchEnd):
            if super().event(event):
                return True

        if event.type() == QEvent.Type.TouchBegin:
            points = event.touchPoints()
            if not points:
                return True

            # First finger pressed becomes the primary finger
            p = points[0]
            self.primary_touch_id = p.id()
            self.drag_start = p.pos()
            self.dragging = True
            self.offset_y = 0
            return True

        elif event.type() == QEvent.Type.TouchUpdate:
            if self.primary_touch_id is None:
                return True

            # Find the point with the primary ID
            for p in event.touchPoints():
                if p.id() == self.primary_touch_id:
                    self.handle_drag(p.pos())
                    break
            return True

        elif event.type() == QEvent.Type.TouchEnd:
            if self.primary_touch_id is not None:
                for p in event.touchPoints():
                    if p.id() == self.primary_touch_id:
                        self.handle_release()
                        break

            self.primary_touch_id = None
            return True

        return super().event(event)

    # ───────────────────────────────────────────────
    # MOUSE SUPPORT (optional but useful on PC)
    # ───────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.primary_touch_id is None:
            self.drag_start = event.pos()
            self.dragging = True
            self.offset_y = 0

    def mouseMoveEvent(self, event):
        if self.dragging and self.primary_touch_id is None:
            self.handle_drag(event.pos())

    def mouseReleaseEvent(self, event):
        if self.dragging and self.primary_touch_id is None:
            self.handle_release()

    # ───────────────────────────────────────────────
    # CORE DRAG LOGIC (shared by mouse + touch)
    # ───────────────────────────────────────────────
    def handle_drag(self, pos):
        dy = pos.y() - self.drag_start.y()

        # Rubber-band effect when dragging beyond limits
        at_top = self.current_index == 0 and dy > 0
        at_bottom = self.current_index == len(self.pages) - 1 and dy < 0

        if at_top or at_bottom:
            dy = dy / (abs(dy) / 150 + 1)

        self.offset_y = dy

        # Move all pages relative to drag
        for i, page in enumerate(self.pages):
            y = (i - self.current_index) * 480 + dy
            page.move(0, y)

    # ───────────────────────────────────────────────
    # RELEASE LOGIC (snap or change page)
    # ───────────────────────────────────────────────
    def handle_release(self):
        dy = self.offset_y
        threshold = 120

        # If dragging out of bounds → snap back
        if (self.current_index == 0 and dy > 0) or \
           (self.current_index == len(self.pages) - 1 and dy < 0):
            self.animate_to(self.current_index)
            self.dragging = False
            return

        # Normal switching
        if dy < -threshold and self.current_index < len(self.pages) - 1:
            self.animate_to(self.current_index + 1)
        elif dy > threshold and self.current_index > 0:
            self.animate_to(self.current_index - 1)
        else:
            # Not enough movement → snap back
            self.animate_to(self.current_index)

        self.dragging = False

    # ───────────────────────────────────────────────
    # ANIMATION HELPER
    # ───────────────────────────────────────────────
    def animate_to(self, target_index):
        self.current_index = target_index

        self.animations.clear()

        for i, page in enumerate(self.pages):
            start_y = page.y()
            end_y = (i - target_index) * 480

            anim = QPropertyAnimation(page, b"pos")
            anim.setDuration(220)
            anim.setStartValue(QPoint(0, start_y))
            anim.setEndValue(QPoint(0, end_y))
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.start()

            self.animations.append(anim)  # store to prevent GC