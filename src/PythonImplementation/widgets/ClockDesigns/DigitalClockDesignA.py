from PySide6.QtGui import QPainter, QPen, QColor, QFontDatabase, QFont
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer

from math import sin, cos, pi
from datetime import datetime

class DigitalClockDesignA(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480,480)

        # humidity label
        time_label = QLabel("15:37", parent=self)
        time_label.setStyleSheet("color: #1F6FEB; background-color: transparent;")
        time_label.setFont(QFontDatabase.font("Seven Segment", "", 140))
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label = time_label

        layout = QVBoxLayout(self)
        layout.addWidget(time_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(500)

    def updateTime(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M"))
        self.update()

    def paintEvent(self, event):
        now = datetime.now()
        now_seconds = now.second

        painter = QPainter()
        painter.begin(self)
        red_pen = QPen(QColor("#c30101"), 3)
        dark_red_pen = QPen(QColor("#7c0101"), 3)
        blue_pen = QPen(QColor("#1F6FEB"), 5)
        dark_blue_pen = QPen(QColor("#1F6FEB").darker(150), 5)

        # CLEAR THE PREVIOUS FRAME
        painter.fillRect(self.rect(), QColor("#000000"))


        # Sekund je 60, kružnice má 360°. 360/60 = 6
        angle_increments = 6
        short_tick_start = 220
        long_tick_start = 210
        distance_from_center_end = 240

        for i in range(0, 60*angle_increments, angle_increments):
            seconds = i / angle_increments
            if seconds % 5 == 0:
                if seconds <= now_seconds:
                    painter.setPen(blue_pen)
                else:
                    painter.setPen(dark_blue_pen)
                distance_from_center_start = long_tick_start
            else:
                if seconds <= now_seconds:
                    painter.setPen(red_pen)
                else:
                    continue
                    #painter.setPen(dark_red_pen)
                distance_from_center_start = short_tick_start

            rad = (i-90) * (pi / 180)
            x_start = int(distance_from_center_start*cos(rad))
            y_start = int(distance_from_center_start*sin(rad))
            x_end = int(distance_from_center_end*cos(rad))
            y_end = int(distance_from_center_end*sin(rad))

            painter.drawLine(x_start + 240, y_start + 240, x_end + 240, y_end + 240)
