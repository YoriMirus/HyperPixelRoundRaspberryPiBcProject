import math

from PySide6.QtCore import QTimer, QPoint, QRectF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap, QPainter, QColor, Qt, QPen

from helpers.SensorManager import SensorManager


class LevelWidget(QWidget):
    def __init__(self, parent=None, sensor_manager=None|SensorManager):
        super(LevelWidget, self).__init__(parent)
        self.setFixedSize(480, 480)
        self.sensor_manager = sensor_manager

        # Timer
        self.timer_refresh_rate = 120
        if sensor_manager is not None:
            self.main_timer = QTimer(self)
            self.main_timer.timeout.connect(self.on_timer_tick)
            self.main_timer.start(int((1.0 / self.timer_refresh_rate) * 1000))

        # Načtení bubliny
        self.bubble_pixmap = QPixmap("assets/bubble.png").scaled(
            60, 60,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Aktuální hodnoty (ve stupních)
        self.roll = -5
        self.pitch = -0

    def set_bubble_position(self, roll, pitch):
        self.roll = roll
        self.pitch = pitch

    def paintEvent(self, event):
        painter = QPainter(self)

        # --- 1) Overlay ---
        painter.setBrush(QColor(255,255,255))
        painter.drawEllipse(0, 0, 480, 480)

        painter.setBrush(QColor(120, 255, 80, 120))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 480, 480)

        # --- 2) Výpočet pozice bubliny ---
        # rozsah ±5°, 42 px na stupeň
        px_per_degree = 34

        center_x = self.width() / 2
        center_y = self.height() / 2

        x = self.roll * px_per_degree
        y = self.pitch * px_per_degree

        # Vzdálenost od středu musí být vždy max 240 - 30 (šířka displeje - šířka bubliny)/2
        xy_vec_size = math.sqrt(x*x+y*y)

        if xy_vec_size > 210:
            offset = xy_vec_size / 210
            x = x/offset
            y = y/offset

        # posun na střed obrázku (ne top-left)
        bubble_w = self.bubble_pixmap.width()
        bubble_h = self.bubble_pixmap.height()

        top_left_x = x + center_x - bubble_w / 2
        top_left_y = y + center_y - bubble_h / 2

        # --- 3) Vykreslení bubliny ---
        painter.drawPixmap(int(top_left_x), int(top_left_y), self.bubble_pixmap)

        painter.setPen(QPen(QColor(0,0,0), 5))
        painter.setBrush(Qt.NoBrush)

        # Vykreslení velkých a malých čár
        for i in range(7):
            if i == 0:
                continue

            small_tick_width = 30

            # Malé čáry
            if i % 2 == 0:
                x_12_start = 240 - (small_tick_width/2)
                x_12_end = 240 + (small_tick_width/2)

                y_1 = 240 - (px_per_degree * i)
                y_2 = 240 + (px_per_degree * i)

                y_34_start = 240 - (small_tick_width/2)
                y_34_end = 240 + (small_tick_width/2)

                x_3 = 240 - (px_per_degree * i)
                x_4 = 240 + (px_per_degree * i)

                painter.drawLine(x_3, y_34_start, x_3, y_34_end)
                painter.drawLine(x_4, y_34_start, x_4, y_34_end)

                painter.drawLine(x_12_start, y_1, x_12_end, y_1)
                painter.drawLine(x_12_start, y_2, x_12_end, y_2)

                continue


            x = int(px_per_degree * i)
            y = int(px_per_degree * i)

            x = 240 - x
            y = 240 - y

            painter.drawEllipse(x, y, i * px_per_degree * 2, i * px_per_degree * 2)

        # Vykreslení kříže
        painter.drawLine(240, 0, 240, 480)
        painter.drawLine(0, 240, 480, 240)
    def on_timer_tick(self):
        if self.sensor_manager.MMA8452Q is None:
            return

        roll, pitch = self.sensor_manager.MMA8452Q.read_gyro()
        self.roll = roll
        self.pitch = pitch
        self.update()