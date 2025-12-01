from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout
)
from PySide6.QtCore import (
    Qt, QTimer, QPointF, QEvent, QPropertyAnimation, QEasingCurve
)
from PySide6.QtGui import QMouseEvent, QTouchEvent, QPainter


class ZoomCarousel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setRenderHints(self.view.renderHints() | QPainter.Antialiasing)

        # MainWindow handles touch until zoom-out
        self.view.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.view.viewport().setAttribute(Qt.WA_AcceptTouchEvents, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self.view.viewport().installEventFilter(self)

        self.proxies = []
        self.current_index = 0
        self.is_zoomed_out = False

        # long press
        self.longPressTimer = QTimer(self)
        self.longPressTimer.setInterval(1000)
        self.longPressTimer.setSingleShot(True)
        self.longPressTimer.timeout.connect(self._on_long_press)

        # interaction state
        self._dragging = False
        self._press_view_x = 0
        self._tap_start_pos = None
        self._primary_touch_id = None
        self._min_drag_to_switch = 120

        # drag multiplier
        self.drag_speed = 2.0

        self._scroll_anim = None
        self._scale_anims = []

    # ---------------------------------------------------------------
    def addWidget(self, widget):
        widget.setFixedSize(480, 480)
        proxy = self.scene.addWidget(widget)
        proxy.setTransformOriginPoint(proxy.boundingRect().center())
        self.proxies.append(proxy)
        self._reposition_items()

    def _reposition_items(self):
        x = 0
        for proxy in self.proxies:
            proxy.setPos(QPointF(x, 0))
            x += 480

        self.scene.setSceneRect(0, 0, x, 480)
        self._center_on_current()

    def _center_on_current(self):
        target_x = self.current_index * 480 + 240
        self.view.centerOn(target_x, 240)

    # ---------------------------------------------------------------
    # Zooming
    # ---------------------------------------------------------------
    def _on_long_press(self):
        if not self.is_zoomed_out:
            self.zoom_out()

    def zoom_out(self):
        if self.is_zoomed_out:
            return

        self.view.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, False)

        for proxy in self.proxies:
            self._run_scale_animation(proxy, proxy.scale(), 0.7)

        self.is_zoomed_out = True

    def zoom_in_to_current(self):
        for proxy in self.proxies:
            self._run_scale_animation(proxy, proxy.scale(), 1.0)

        self.is_zoomed_out = False
        self._animate_scroll_to_current()
        self.view.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def _run_scale_animation(self, proxy, start, end):
        anim = QPropertyAnimation(proxy, b"scale")
        anim.setDuration(350)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        self._scale_anims.append(anim)
        anim.finished.connect(lambda: self._scale_anims.remove(anim))
        anim.start()

    # ---------------------------------------------------------------
    # Event Filter: Mouse + Touch Support
    # ---------------------------------------------------------------
    def eventFilter(self, obj, ev):
        if obj is not self.view.viewport():
            return False

        if not self.is_zoomed_out:
            return False

        et = ev.type()

        # -----------------------------------------------------------
        # TOUCH HANDLING
        # -----------------------------------------------------------
        if et == QEvent.TouchBegin:
            points = ev.touchPoints()
            if not points:
                return False

            p = points[0]
            self._primary_touch_id = p.id()
            self._dragging = True
            self._press_view_x = self.view.horizontalScrollBar().value()
            self._tap_start_pos = p.pos().toPoint()

            return True

        elif et == QEvent.TouchUpdate and self._primary_touch_id is not None:
            for p in ev.touchPoints():
                if p.id() == self._primary_touch_id:
                    view_dx = p.pos().x() - self._tap_start_pos.x()
                    delta = view_dx * self.drag_speed

                    self.view.horizontalScrollBar().setValue(
                        int(self._press_view_x - delta)
                    )
                    return True

        elif et == QEvent.TouchEnd and self._primary_touch_id is not None:
            for p in ev.touchPoints():
                if p.id() == self._primary_touch_id:
                    self._finish_drag(p.pos().toPoint())
                    break

            self._primary_touch_id = None
            return True

        # -----------------------------------------------------------
        # MOUSE HANDLING
        # -----------------------------------------------------------
        if isinstance(ev, QMouseEvent):

            if et == QEvent.MouseButtonPress:
                self._dragging = True
                self._press_view_x = self.view.horizontalScrollBar().value()
                self._tap_start_pos = ev.pos()
                return True

            elif et == QEvent.MouseMove and self._dragging:
                view_dx = ev.pos().x() - self._tap_start_pos.x()
                delta = view_dx * self.drag_speed
                self.view.horizontalScrollBar().setValue(
                    int(self._press_view_x - delta)
                )
                return True

            elif et == QEvent.MouseButtonRelease and self._dragging:
                self._finish_drag(ev.pos())
                return True

        return False

    # ---------------------------------------------------------------
    # Shared drag-release logic (mouse + touch)
    # ---------------------------------------------------------------
    def _finish_drag(self, end_pos):
        self._dragging = False
        scrollbar = self.view.horizontalScrollBar()
        delta = scrollbar.value() - self._press_view_x

        # Tap?
        if (end_pos - self._tap_start_pos).manhattanLength() < 15:
            self.zoom_in_to_current()
            return

        # Swipe?
        if delta > self._min_drag_to_switch and self.current_index < len(self.proxies) - 1:
            self._go_next()

        elif delta < -self._min_drag_to_switch and self.current_index > 0:
            self._go_prev()

        else:
            self._animate_scroll_to_current()

    # ---------------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------------
    def _go_next(self):
        self.current_index += 1
        self._animate_scroll_to_current()

    def _go_prev(self):
        self.current_index -= 1
        self._animate_scroll_to_current()

    def _animate_scroll_to_current(self):
        target_center = self.current_index * 480 + 240
        target_scroll = target_center - (self.view.width() // 2)

        scrollbar = self.view.horizontalScrollBar()

        if self._scroll_anim:
            self._scroll_anim.stop()

        anim = QPropertyAnimation(scrollbar, b"value")
        anim.setDuration(320)
        anim.setStartValue(scrollbar.value())
        anim.setEndValue(target_scroll)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

        self._scroll_anim = anim
