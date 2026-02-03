from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QEvent, QTimer

from widgets.SensorWidgets.ArtificialHorizonWidget import ArtificialHorizonWidget
from widgets.ClockDesigns.AnalogClock import AnalogClock
from widgets.ClockDesigns.DigitalClockDesignA import DigitalClockDesignA
from widgets.SensorWidgets.WeatherStationWidget import WeatherStationWidget
from widgets.Other.QuitWidget import QuitWidget
from widgets.Layouts.ZoomCarousel import ZoomCarousel
from widgets.Other.DebugInfo import DebugInfo

class SlidingLayout(QWidget):
    def __init__(self, is_raspberry_pi=False, sensorManager=None):
        super().__init__()
        self.sensorManager = sensorManager

        self.setFixedSize(480, 480)
        self.setStyleSheet("QWidget { background-color: black; }")
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)  # Enable multitouch

        clock_container = ZoomCarousel()
        clock_container.addWidget(AnalogClock())
        clock_container.addWidget(DigitalClockDesignA())

        self.pages = [
            QuitWidget(),
            clock_container,
            WeatherStationWidget(self.sensorManager),
            ArtificialHorizonWidget(self.sensorManager),
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

        # long press
        self.longPressTimer = QTimer(self)
        self.longPressTimer.setInterval(1000)
        self.longPressTimer.setSingleShot(True)
        self.longPressTimer.timeout.connect(self.on_long_press)


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
            self.handle_press(p.pos())
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
            self.handle_press(event.pos())

    def mouseMoveEvent(self, event):
        if self.dragging and self.primary_touch_id is None:
            self.handle_drag(event.pos())

    def mouseReleaseEvent(self, event):
        if self.dragging and self.primary_touch_id is None:
            self.handle_release()

    # ───────────────────────────────────────────────
    # CORE DRAG LOGIC (shared by mouse + touch)
    # ───────────────────────────────────────────────
    def on_long_press(self):
        threshold = 20
        if self.offset_y > threshold:
            return

        self.handle_release()

        active_widget = self.pages[self.current_index]
        try:
            active_widget.on_long_press()
        except AttributeError:
            print("This widget does not support long presses")
            pass

    def handle_press(self, pos):
        self.drag_start = pos
        self.dragging = True
        self.offset_y = 0
        self.longPressTimer.start()

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
        self.longPressTimer.stop()
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