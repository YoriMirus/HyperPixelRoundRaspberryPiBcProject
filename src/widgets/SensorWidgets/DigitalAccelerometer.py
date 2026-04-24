import math

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont


class DigitalAccelerometerExample(QWidget):
    def __init__(self, parent=None, sensor_manager=None):
        super().__init__(parent)
        self.setFixedSize(480, 480)
        self.sensor_manager = sensor_manager

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: black;")

        # Values (RENAMED to avoid QWidget conflicts)
        self.accel_x = 0.0
        self.accel_y = 0.0
        self.accel_z = 0.0
        self.roll = 0.0
        self.pitch = 0.0

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

        painter.setPen(QColor(220, 220, 220))

        title_font = QFont("Arial", 20, QFont.Bold)
        value_font = QFont("Arial", 18)

        center_x = self.width() // 2
        y_pos = 80  # renamed to avoid confusion

        # Zrychlení
        painter.setFont(title_font)
        painter.drawText(0, y_pos, 480, 40, Qt.AlignCenter, "ZRYCHLENÍ")
        y_pos += 50

        painter.setFont(value_font)
        painter.drawText(0, y_pos, 480, 30, Qt.AlignCenter, f"X: {self.accel_x:.3f}")
        y_pos += 35
        painter.drawText(0, y_pos, 480, 30, Qt.AlignCenter, f"Y: {self.accel_y:.3f}")
        y_pos += 35
        painter.drawText(0, y_pos, 480, 30, Qt.AlignCenter, f"Z: {self.accel_z:.3f}")
        y_pos += 60

        # Orientace
        painter.setFont(title_font)
        painter.drawText(0, y_pos, 480, 40, Qt.AlignCenter, "ORIENTACE")
        y_pos += 50

        painter.setFont(value_font)
        painter.drawText(0, y_pos, 480, 30, Qt.AlignCenter, f"Náklon:  {self.roll:.2f}°")
        y_pos += 35
        painter.drawText(0, y_pos, 480, 30, Qt.AlignCenter, f"Klopení: {self.pitch:.2f}°")

    def on_timer_tick(self):
        if self.sensor_manager.MMA8452Q is None:
            return

        try:
            self.accel_x, self.accel_y, self.accel_z = \
                self.sensor_manager.MMA8452Q.read_acceleration()
        except:
            pass

        try:
            roll, pitch = self.sensor_manager.MMA8452Q.read_gyro_level()
            self.roll = roll
            self.pitch = pitch
        except:
            pass

        self.update()