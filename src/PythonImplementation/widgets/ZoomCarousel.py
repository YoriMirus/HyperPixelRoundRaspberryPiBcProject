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

        self._bounce_distance = 80
        self._bounce_duration = 300

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setRenderHints(self.view.renderHints() | QPainter.Antialiasing)
        self.view.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        # capture gestures from viewport instead of container
        self.view.viewport().installEventFilter(self)

        self.proxies = []
        self.current_index = 0
        self.is_zoomed_out = False

        # long press
        self.longPressTimer = QTimer(self)
        self.longPressTimer.setInterval(1000)
        self.longPressTimer.setSingleShot(True)
        self.longPressTimer.timeout.connect(self._on_long_press)

        # swipe state
        self._press_scene_x = None
        self._press_view_x = None
        self._dragging = False
        self._min_drag_to_switch = 120   # pixels

        # persistent animation reference
        self._scroll_anim = None
        self._scale_anims = []
        self._tap_start_pos = None
        self._tap_threshold = 15  # px

    # ---------------------------------------------------------------
    # Add a widget into the horizontal strip
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
            x += 480  # fixed width

        self.scene.setSceneRect(0, 0, x, 480)
        self._center_on_current()

    def _center_on_current(self):
        if not self.proxies:
            return
        target_x = self.current_index * 480 + 240
        self.view.centerOn(target_x, 240)

    # ---------------------------------------------------------------
    # Long press → zoom out
    # ---------------------------------------------------------------
    def _on_long_press(self):
        if self.is_zoomed_out:
            return
        self.zoom_out()

    def zoom_out(self):
        if self.is_zoomed_out:
            return

        self.view.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, False)

        for proxy in self.proxies:
            proxy.setTransformOriginPoint(proxy.boundingRect().center())
            self._run_scale_animation(proxy, proxy.scale(), 0.7)

        self.is_zoomed_out = True

    def zoom_in_to_current(self):
        """Zoom in only the currently selected widget."""
        for i, proxy in enumerate(self.proxies):
            proxy.setTransformOriginPoint(proxy.boundingRect().center())
            # keep it uniform: scale everything back to 1.0
            target = 1.0
            self._run_scale_animation(proxy, proxy.scale(), target)

        self.is_zoomed_out = False
        self._animate_scroll_to_current()
        self.view.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, True)

    # ---------------------------------------------------------------
    # Scaling animation
    # ---------------------------------------------------------------
    def _run_scale_animation(self, proxy, start, end):
        anim = QPropertyAnimation(proxy, b"scale")
        anim.setDuration(350)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        # Keep reference so GC doesn't kill animations
        self._scale_anims.append(anim)

        # Remove from list when finished
        anim.finished.connect(lambda: self._scale_anims.remove(anim))

        anim.start()

    # ---------------------------------------------------------------
    # Swiping / drag logic (no overscroll transform)
    # ---------------------------------------------------------------
    def eventFilter(self, obj, ev):
        try:
            if obj is not self.view.viewport():
                return False

            et = ev.type()

            # ----------------------------------------------------------
            # ZOOMED OUT → swipe / tap mode
            # ----------------------------------------------------------
            if et == QEvent.MouseButtonPress:
                if isinstance(ev, QMouseEvent):
                    self._dragging = True
                    self._press_scene_x = self.view.mapToScene(ev.pos()).x()
                    self._press_view_x = self.view.horizontalScrollBar().value()

                    # tap detection begins here
                    self._tap_start_pos = ev.pos()

                self.longPressTimer.stop()
                return True

            elif et == QEvent.MouseMove and self._dragging:
                if isinstance(ev, QMouseEvent):
                    cur_scene_x = self.view.mapToScene(ev.pos()).x()
                    delta = (self._press_scene_x - cur_scene_x)

                    # live dragging — clamp via scrollbar's natural bounds
                    self.view.horizontalScrollBar().setValue(
                        int(self._press_view_x + delta)
                    )
                return True

            elif et == QEvent.MouseButtonRelease and self._dragging:
                self._dragging = False

                current_scroll = self.view.horizontalScrollBar().value()
                delta = current_scroll - self._press_view_x

                # -------------------------
                # 1. TAP?  (short movement)
                # -------------------------
                if self._tap_start_pos is not None and \
                        (ev.pos() - self._tap_start_pos).manhattanLength() < self._tap_threshold:
                    # tap-to-zoom-in behavior
                    self.zoom_in_to_current()
                    return True

                # -------------------------
                # 2. SWIPE LEFT / RIGHT?
                # -------------------------
                if delta > self._min_drag_to_switch and self.current_index < len(self.proxies) - 1:
                    self._go_next()

                elif delta < -self._min_drag_to_switch and self.current_index > 0:
                    self._go_prev()
                else:
                    self._animate_scroll_to_current()

                return True

            return super().eventFilter(obj, ev)

        except Exception:
            import traceback;
            traceback.print_exc()
            return False

    # ---------------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------------
    def _go_next(self):
        if self.current_index < len(self.proxies) - 1:
            self.current_index += 1
        self._animate_scroll_to_current()

    def _go_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
        self._animate_scroll_to_current()

    def _snap_back(self):
        self._animate_scroll_to_current()

    # ---------------------------------------------------------------
    # Smooth scrolling animation
    # ---------------------------------------------------------------
    def _animate_scroll_to_current(self):
        target_center_x = self.current_index * 480 + 240
        target_scroll = target_center_x - (self.view.width() // 2)

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
