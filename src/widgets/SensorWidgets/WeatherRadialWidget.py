import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QPen


class WeatherRadialWidget(QWidget):
    def __init__(self, sensorManager):
        super().__init__()
        self.sensorManager = sensorManager

        self.value = 0
        self.temperature = 0.0
        self.setFixedSize(480, 480)
        self.setWindowTitle("Humidity Dial")

        # Poll sensor every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_sensor)
        self.timer.start(1000)

    # ---------- Sensor ----------
    def update_sensor(self):
        if self.sensorManager.SHT3x is None:
            return

        try:
            temp, humidity = self.sensorManager.SHT3x.read_measurement()

            # clamp + normalize
            self.value = max(0, min(100, int(humidity)))
            self.temperature = temp

            self.update()  # trigger repaint

        except Exception as e:
            print(e)

    # ---------- Rendering ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        center = rect.center()

        pen_width = 10
        radius = min(rect.width(), rect.height()) / 2 - (pen_width / 2)

        outer_rect = QRectF(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2
        )

        # Background
        painter.setBrush(QColor("#1e1e2f"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(outer_rect)

        # Color based on humidity
        if self.value < 30:
            color = QColor("#f39c12")
        elif self.value < 60:
            color = QColor("#00c2ff")
        else:
            color = QColor("#3498db")

        # Arc
        pen = QPen(color, pen_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        span_angle = int((self.value / 100) * 360 * 16)

        if self.value == 100:
            # avoid tiny Qt gap at full circle
            painter.drawEllipse(outer_rect)
        else:
            painter.drawArc(outer_rect, 270 * 16, -span_angle)

        # Inner circle
        painter.setBrush(QColor("#2d2d44"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius - 20, radius - 20)

        # Text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 60, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{self.temperature:.1f}°C")