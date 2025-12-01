from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QVBoxLayout
)
from PySide6.QtCore import (
    Qt, QTimer, QPointF, QEvent, QPropertyAnimation, QEasingCurve
)
from PySide6.QtGui import QMouseEvent, QPainter


class ZoomCarousel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setRenderHints(self.view.renderHints() | QPainter.Antialiasing)

        # By default: transparent, MainWindow handles touch
        self.view.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        # We receive events when zoomed out only
        self.view.viewport().installEventFilter(self)

        self.proxies = []
        self.current_index = 0
        self.is_zoomed_out = False

        # long press
        self.longPressTimer = QTimer(self)
        self.longPressTimer.setInterval(1000)
        self.longPressTimer.setSingleShot(True)
        self.longPressTimer.timeout.connect(self._on_long_press)

        # touch/mouse dragging state
        self._dragging = False
        self._press_view_x = 0
        self._tap_start_pos = None
        self._min_drag_to_switch = 120

        self.drag_speed = 1.0

        # animations
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
        if not self.proxies:
            return
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

        # Allow the carousel to receive events
        self.view.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, False)

        for proxy in self.proxies:
            proxy.setTransformOriginPoint(proxy.boundingRect().center())
            self._run_scale_animation(proxy, proxy.scale(), 0.7)

        self.is_zoomed_out = True

    def zoom_in_to_current(self):
        for proxy in self.proxies:
            proxy.setTransformOriginPoint(proxy.boundingRect().center())
            self._run_scale_animation(proxy, proxy.scale(), 1.0)

        self.is_zoomed_out = False
        self._animate_scroll_to_current()

        # Give control back to MainWindow
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
    # Event Filter: Handling swipe / tap in zoomed-out mode
    # ---------------------------------------------------------------
    def eventFilter(self, obj, ev):
        if obj is not self.view.viewport():
            return False

        # Only handle input when zoomed out
        if not self.is_zoomed_out:
            return False

        et = ev.type()

        # -----------------------------------------
        # Press
        # -----------------------------------------
        if et == QEvent.MouseButtonPress:
            if isinstance(ev, QMouseEvent):
                self._dragging = True
                self._press_view_x = self.view.horizontalScrollBar().value()
                self._tap_start_pos = ev.pos()

            return True

        # -----------------------------------------
        # Move  (drag)
        # -----------------------------------------
        elif et == QEvent.MouseMove and self._dragging:
            if isinstance(ev, QMouseEvent):
                # Use *view space* delta
                view_dx = ev.pos().x() - self._tap_start_pos.x()

                # Apply multiplier
                delta = view_dx * self.drag_speed

                # Update scrollbar directly
                self.view.horizontalScrollBar().setValue(
                    int(self._press_view_x - delta)
                )
            return True

        # -----------------------------------------
        # Release
        # -----------------------------------------
        elif et == QEvent.MouseButtonRelease and self._dragging:
            self._dragging = False

            scrollbar = self.view.horizontalScrollBar()
            delta = scrollbar.value() - self._press_view_x

            # Tap?
            if self._tap_start_pos is not None and \
               (ev.pos() - self._tap_start_pos).manhattanLength() < 15:
                self.zoom_in_to_current()
                return True

            # Swipe?
            if delta > self._min_drag_to_switch and self.current_index < len(self.proxies) - 1:
                self._go_next()

            elif delta < -self._min_drag_to_switch and self.current_index > 0:
                self._go_prev()

            else:
                self._animate_scroll_to_current()

            return True

        return False

    # ---------------------------------------------------------------
    # Navigation helpers
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
