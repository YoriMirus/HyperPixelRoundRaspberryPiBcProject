import math

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont

from sensors.MMA8452Q import MMA8452Q


class DigitalAccelerometerExample(QWidget):
    def __init__(self, parent=None, sensor_manager=None):
        super().__init__(parent)
        self.setFixedSize(480, 480)
        self.sensor_manager = sensor_manager

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: black;")

        # Values
        self.x = 0
        self.y = 0
        self.z = 0
        self.roll = 0
        self.pitch = 0

        # Timer
        self.timer_refresh_rate = 30
        if sensor_manager is not None:
            self.main_timer = QTimer(self)
            self.main_timer.timeout.connect(self.on_timer_tick)
            self.main_timer.start(int((1.0 / self.timer_refresh_rate) * 1000))

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setBrush(QColor("black"))
        painter.drawEllipse(0, 0, 480, 480)

        # Text
        painter.setPen(QColor(220, 220, 220))

        title_font = QFont("Arial", 20, QFont.Bold)
        value_font = QFont("Arial", 18)

        center_x = self.width() // 2
        y = 80

        # Zrychlení
        painter.setFont(title_font)
        painter.drawText(0, y, 480, 40, Qt.AlignCenter, "ZRYCHLENÍ")
        y += 50

        painter.setFont(value_font)
        painter.drawText(0, y, 480, 30, Qt.AlignCenter, f"X: {self.x:.3f}")
        y += 35
        painter.drawText(0, y, 480, 30, Qt.AlignCenter, f"Y: {self.y:.3f}")
        y += 35
        painter.drawText(0, y, 480, 30, Qt.AlignCenter, f"Z: {self.z:.3f}")
        y += 60

        # Orientace
        painter.setFont(title_font)
        painter.drawText(0, y, 480, 40, Qt.AlignCenter, "ORIENTACE")
        y += 50

        painter.setFont(value_font)
        painter.drawText(0, y, 480, 30, Qt.AlignCenter, f"Náklon:  {self.roll:.2f}°")
        y += 35
        painter.drawText(0, y, 480, 30, Qt.AlignCenter, f"Klopení: {self.pitch:.2f}°")

    def on_timer_tick(self):
        if self.sensor_manager.MMA8452Q is None:
            return

        # Example: adjust depending on your actual API
        try:
            self.x, self.y, self.z = self.sensor_manager.MMA8452Q.read_acceleration()
        except:
            pass

        try:
            roll, pitch = self.sensor_manager.MMA8452Q.read_gyro()
            self.roll = roll
            self.pitch = pitch
        except:
            pass

        self.update()