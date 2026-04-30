import math
import time

from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QFont


class GalbraigthGraphTemp(QWidget):
    def __init__(self, sensorManager, min_temp=-30, max_temp=70, parent=None):
        super().__init__(parent)

        self.sensorManager = sensorManager
        self.setFixedSize(480, 480)

        self.min_temp = min_temp
        self.max_temp = max_temp

        self.temperature = 0.0

        # Data storage (time, temperature)
        self.samples = []
        self.start_time = time.time()

        self.start_time = time.time()
        self.start_second = int(self.start_time % 60)

        self.last_sec = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_sensor)
        self.timer.start(100)

    def update_sensor(self):
        if self.sensorManager.SHT3x is None:
            return

        try:
            temp, _ = self.sensorManager.SHT3x.read_measurement()

            self.temperature = temp

            current_time = time.time()
            current_sec = current_time % 60.0

            # detect wrap (crossing top / 0 sec)
            if self.last_sec is not None:
                if current_sec < self.last_sec:
                    # we crossed from ~59 → 0 (top of graph)
                    self.samples.clear()

            self.last_sec = current_sec

            # store absolute second
            self.samples.append((current_sec, temp))

            self.update()

        except Exception as e:
            print(e)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        font = QFont()
        font.setPointSize(16)
        painter.setFont(font)

        w, h = self.width(), self.height()
        radius = min(w, h) / 2 - 30  # extra margin for labels
        center_x = w / 2
        center_y = h / 2

        painter.translate(center_x, center_y)

        def temp_to_radius(temp):
            norm = (temp - self.min_temp) / (self.max_temp - self.min_temp)
            norm = max(0.0, min(1.0, norm))
            return norm * radius

        # ---------- outer circle ----------
        painter.setPen(QPen(Qt.gray, 2))
        painter.drawEllipse(QPointF(0, 0), radius, radius)

        # ---------- radial scale (temperature rings) ----------
        painter.setPen(QPen(QColor(80, 80, 80), 1, Qt.DashLine))

        fm = painter.fontMetrics()

        steps = 5
        for i in range(steps):
            t = self.min_temp + i * (self.max_temp - self.min_temp) / steps
            r = temp_to_radius(t)

            painter.setPen(QPen(QColor(80, 80, 80), 1, Qt.DashLine))
            painter.drawEllipse(QPointF(0, 0), r, r)

            label = f"{t:.0f}°"
            painter.setPen(Qt.white)

            w = fm.horizontalAdvance(label)
            h = fm.height()

            margin = 6  # space from axis

            x = -margin - w  # fully left of axis
            y = -r + h / 4  # baseline-correct vertical position

            painter.drawText(x, y, label)

        # ---------- 0°C reference circle ----------
        if self.min_temp <= 0 <= self.max_temp:
            r0 = temp_to_radius(0)
            painter.setPen(QPen(QColor(0, 150, 255), 2))  # distinct color
            painter.drawEllipse(QPointF(0, 0), r0, r0)

        # ---------- 0-second axis (top vertical line) ----------
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawLine(0, 0, 0, -radius)

        # ---------- clock-style angular labels ----------
        painter.setPen(Qt.white)
        font = QFont()
        font.setPointSize(20)
        painter.setFont(font)

        label_radius = radius + 15  # slightly outside the circle

        fm = painter.fontMetrics()

        for i in range(12):
            angle = (i / 12) * 2 * math.pi - math.pi / 2
            label = "12" if i == 0 else str(i)

            x = label_radius * math.cos(angle)
            y = label_radius * math.sin(angle)

            # text dimensions
            w = fm.horizontalAdvance(label)
            h = fm.height()

            # center text properly
            tx = x - w / 2
            ty = y + h / 4  # better optical centering than h/2

            painter.drawText(tx, ty, label)

        painter.setPen(QPen(QColor(80, 80, 80), 1, Qt.DashLine))
        for i in range(12):  # every 10 seconds
            angle = (i / 12) * 2 * math.pi - math.pi / 2
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            painter.drawLine(0, 0, x, y)

        if len(self.samples) < 2:
            return

        painter.setPen(QPen(QColor(0, 255, 100), 2))
        points = []
        for t, temp in self.samples:
            absolute_sec = (self.start_second + t) % 60.0

            #angle = (absolute_sec / 60.0) * 2 * math.pi - math.pi / 2
            angle = (t / 60.0) * 2 * math.pi - math.pi / 2

            r = temp_to_radius(temp)

            x = r * math.cos(angle)
            y = r * math.sin(angle)

            points.append(QPointF(x, y))


        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])

        last_point = points[-1]
        painter.setBrush(QColor(255, 50, 50))
        painter.drawEllipse(last_point, 4, 4)