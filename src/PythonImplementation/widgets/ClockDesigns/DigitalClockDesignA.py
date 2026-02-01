from PySide6.QtGui import QPainter, QPen, QColor, QFontDatabase, QFont
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSpacerItem, QSizePolicy, QHBoxLayout, QFrame
from PySide6.QtCore import Qt, QTimer

from math import sin, cos, pi
from datetime import datetime
class DigitalClockDesignA(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480,480)
        self.setStyleSheet("background-color: black")

        self.date_label = QLabel("01 Jan 2025", parent=self)
        self.date_label.setStyleSheet("color: #E0E0E0; background-color: transparent; margin-top: -10px; margin-bottom: -10px;")
        self.date_label.setFont(QFontDatabase.font("Digital-7 Mono", "", 80))
        self.date_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.date_label.setFixedSize(480,100)

        time_layout = QHBoxLayout()
        time_layout.setSpacing(0)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Musíme nastavit záporné marže protože samotný font používá nějaký padding na sobě nebo něco takového. Takže label bere více místa než potřebuje
        # Tímhletím to místo zmenšíme
        # POZOR! Pokud se změní velikost fontu, bude nutné tyto marže opět upravit! Tyto marže fungují dobře pro 130 font size.
        time_style = "color: #1F6FEB; background: transparent; margin-top: -20px; margin-bottom: -20px; margin-left: -40px; margin-right:-40px;"

        self.hour_label = QLabel("16")
        self.hour_label.setFont(QFontDatabase.font("Digital-7 Mono", "", 130))
        self.hour_label.setStyleSheet(time_style)
        self.hour_label.setFixedWidth(200)
        self.hour_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.minute_label = QLabel("47")
        self.minute_label.setFont(QFontDatabase.font("Digital-7 Mono", "", 130))
        self.minute_label.setStyleSheet(time_style)
        self.minute_label.setFixedWidth(200)
        self.minute_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        seperator_label = QLabel(":")
        seperator_label.setFont(QFontDatabase.font("Digital-7 Mono", "", 130))
        seperator_label.setStyleSheet(time_style)

        time_layout.addWidget(self.hour_label)
        time_layout.addWidget(seperator_label)
        time_layout.addWidget(self.minute_label)

        day_label_layout = QHBoxLayout()
        day_label_layout.setSpacing(0)
        day_label_layout.setContentsMargins(0,0,0,0)
        day_label_layout.setAlignment(Qt.AlignCenter)
        self.day_label_layout = day_label_layout
        self.day_labels = []

        days_of_week = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
        for i in range(len(days_of_week)):
            label = QLabel(days_of_week[i])
            label.setStyleSheet("color: #E0E0E0; background-color: transparent;")
            label.setFont(QFont("Sans Serif", 24))
            label.setFixedHeight(100)
            label.setFixedWidth(45)
            label.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.day_labels.append(label)
            day_label_layout.addWidget(label)

        layout = QVBoxLayout(self)
        layout.addWidget(self.date_label)
        layout.addLayout(time_layout)
        layout.addLayout(day_label_layout)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(500)

        self.updateTime()

    def updateTime(self):
        now = datetime.now()

        self.hour_label.setText(now.strftime("%H"))
        self.minute_label.setText(now.strftime("%M"))
        self.date_label.setText(now.strftime("%d-%m"))   # e.g. "10 Jan 2025"

        for i in range(len(self.day_labels)):
            if i == now.weekday():
                self.day_labels[i].setStyleSheet("color: #E0E0E0; background-color: transparent")
            else:
                self.day_labels[i].setStyleSheet("color: #666666; background-color: transparent")
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

        angle_increments = 6
        short_tick_start = 220
        long_tick_start = 210
        distance_from_center_end = 240

        for i in range(0, 360, angle_increments):
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
                    # Skip drawing dark red ticks (you currently skip them)
                    continue
                distance_from_center_start = short_tick_start

            rad = (i - 90) * (pi / 180)
            x_start = int(distance_from_center_start * cos(rad))
            y_start = int(distance_from_center_start * sin(rad))
            x_end = int(distance_from_center_end * cos(rad))
            y_end = int(distance_from_center_end * sin(rad))

            painter.drawLine(x_start + 240, y_start + 240, x_end + 240, y_end + 240)
