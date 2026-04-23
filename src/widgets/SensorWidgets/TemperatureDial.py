import sys
import math
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QPolygon, QFont
from PySide6.QtCore import Qt, QRect, QPoint, QRectF, QTimer


class TemperatureDial(QWidget):
    def __init__(self, sensorManager, min_temp=-20, max_temp=60, parent=None):
        super().__init__(parent)

        self.sensorManager = sensorManager
        self.setFixedSize(480, 480)

        # Configurable range
        self.min_temp = min_temp
        self.max_temp = max_temp

        # State
        self.temperature = 0.0
        self.humidity = 0.0

        # Timer (sensor polling)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_sensor)
        self.timer.start(100)

    # ---------- Sensor ----------
    def update_sensor(self):
        if self.sensorManager.SHT3x is None:
            return

        try:
            temp, humidity = self.sensorManager.SHT3x.read_measurement()

            self.temperature = temp
            self.humidity = humidity

            self.update()

        except Exception as e:
            print(e)

    # ---------- Mapping ----------
    def temp_to_angle(self):
        # Clamp temperature
        t = max(self.min_temp, min(self.max_temp, self.temperature))

        # Normalize
        ratio = (t - self.min_temp) / (self.max_temp - self.min_temp)

        # Map to 270° sweep starting at 135°
        return 135 + (ratio * 270)

    # ---------- Rendering ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # Background
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, 480, 480)

        # Outer ring
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.drawEllipse(0, 0, 480, 480)

        # Move origin to center
        painter.translate(240, 240)

        # ---------- Arcs ----------
        tick_count = 9
        step_angle = 270 / (tick_count - 1)

        blue_steps = 2
        red_steps = 2
        total_steps = tick_count - 1
        white_steps = total_steps - blue_steps - red_steps

        arc_rect = QRect(-220, -220, 440, 440)
        start_angle_deg = 225

        def deg_to_qt(deg):
            return int(deg * 16)

        # WHITE (middle)
        painter.setPen(QPen(QColor(255, 255, 255), 8))
        painter.drawArc(
            arc_rect,
            deg_to_qt(start_angle_deg - blue_steps * step_angle),
            -deg_to_qt(white_steps * step_angle)
        )

        # BLUE (start)
        painter.setPen(QPen(QColor(0, 0, 255), 8))
        painter.drawArc(
            arc_rect,
            deg_to_qt(start_angle_deg),
            -deg_to_qt(blue_steps * step_angle)
        )

        # RED (end)
        painter.setPen(QPen(QColor(255, 0, 0), 8))
        painter.drawArc(
            arc_rect,
            deg_to_qt(start_angle_deg - (blue_steps + white_steps) * step_angle),
            -deg_to_qt(red_steps * step_angle)
        )

        # ---------- Ticks ----------
        painter.setFont(QFont("Arial", 24, QFont.Bold))


        for i in range(tick_count):
            angle_deg = 135 + (i * step_angle)
            angle_rad = math.radians(angle_deg)

            color = QColor(255, 255, 255)
            if i <= blue_steps:
                color = QColor(0, 0, 255)
            elif i >= blue_steps + white_steps:
                color = QColor(255, 0, 0)

            painter.setPen(QPen(color, 4))

            # Tick
            painter.save()
            painter.rotate(angle_deg)
            painter.drawLine(220, 0, 190, 0)
            painter.restore()

            # Label
            val = str(int(self.min_temp + (i / (tick_count - 1)) * (self.max_temp - self.min_temp)))
            tx = 165 * math.cos(angle_rad)
            ty = 165 * math.sin(angle_rad)

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(QRectF(tx - 25, ty - 15, 50, 30), Qt.AlignCenter, val)

        # ---------- Center text ----------
        painter.setFont(QFont("Arial", 36, QFont.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, 60, 200, 60), Qt.AlignCenter, f"{self.temperature:.1f}°C")

        # ---------- Needle ----------
        angle = self.temp_to_angle()

        painter.save()
        painter.rotate(angle)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawPolygon(QPolygon([
            QPoint(-50, -10),
            QPoint(200, 0),
            QPoint(-50, 10)
        ]))

        painter.restore()

        # ---------- Center cap ----------
        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(-30, -30, 60, 60)