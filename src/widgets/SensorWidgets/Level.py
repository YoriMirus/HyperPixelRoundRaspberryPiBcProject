import math

from PySide6.QtCore import QTimer, QPoint, QRectF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap, QPainter, QColor, Qt, QPen, QFontMetrics

from helpers.SensorManager import SensorManager


class LevelWidget(QWidget):
    def __init__(self, parent=None, sensor_manager=None):
        super(LevelWidget, self).__init__(parent)
        self.setFixedSize(480, 480)
        self.sensor_manager = sensor_manager

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

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
        self.roll = -3
        self.pitch = 4

    def set_bubble_position(self, roll, pitch):
        self.roll = roll
        self.pitch = pitch

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setBrush(QColor(180, 255, 120))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 480, 480)

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

        # Vykreslení bubliny
        painter.drawPixmap(int(top_left_x), int(top_left_y), self.bubble_pixmap)

        painter.setPen(QPen(QColor(0,0,0), 5))
        painter.setBrush(Qt.NoBrush)

        # Vykreslení kříže
        painter.drawLine(240, 0, 240, 480)
        painter.drawLine(0, 240, 480, 240)

        # Vykreslení velkých a malých čár
        # Velké čáry
        painter.translate(240, 240)
        painter.drawEllipse(-px_per_degree, -px_per_degree, px_per_degree * 2, px_per_degree * 2)
        painter.drawEllipse(-px_per_degree * 3, -px_per_degree * 3, px_per_degree * 3 * 2, px_per_degree * 3 * 2)
        painter.drawEllipse(-px_per_degree * 5, -px_per_degree * 5, px_per_degree * 5 * 2, px_per_degree * 5 * 2)

        # Malé čáry
        font = painter.font()
        font.setPointSize(24)
        painter.setFont(font)
        fm = QFontMetrics(painter.font())
        small_tick_width = 30
        for i in range(4):
            x_start = -small_tick_width/2
            x_end = small_tick_width/2

            y_1 = -px_per_degree * 2
            y_2 = -px_per_degree * 4
            y_3 = -px_per_degree * 6

            painter.drawLine(x_start, y_1, x_end, y_1)
            painter.drawLine(x_start, y_2, x_end, y_2)
            painter.drawLine(x_start, y_3, x_end, y_3)

            # --- TEXT DRAWING ---
            labels = [("2°", y_1), ("4°", y_2), ("6°", y_3)]

            for text, y in labels:
                text_width = fm.horizontalAdvance(text)
                text_height = fm.height()

                # Position text slightly to the right of the tick
                x_text = x_end + 5

                # Align vertically: shift by half height, but compensate for baseline
                y_text = y + text_height / 2 - fm.descent()

                painter.drawText(x_text, y_text, text)

            painter.rotate(90)

        return

    def on_timer_tick(self):
        if self.sensor_manager.MMA8452Q is None:
            return

        roll, pitch = self.sensor_manager.MMA8452Q.read_gyro_level()
        self.roll = -roll
        self.pitch = pitch
        self.update()