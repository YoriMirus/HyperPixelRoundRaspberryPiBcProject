from PySide6.QtCore import Qt
from PySide6.QtCore import QPoint, QTimer
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics
from PySide6.QtWidgets import QWidget

from helpers.SensorManager import SensorManager
from sensors.Bmp180 import Bmp180


class Barometer(QWidget):
    def __init__(self, parent=None, sensor_manager=None):
        super().__init__(parent)

        self.sensor_manager = sensor_manager

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: black;")

        self.min_pressure = 975
        self.max_pressure = 1045

        self.setFixedSize(480,480)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)


    def paintEvent(self, event):
        if self.sensor_manager.Bmp180 is None:
            press = 1025
        else:
            # Tlak je v Pa, my potřebujeme hPa
            press = self.sensor_manager.Bmp180.read_measurement() / 100

        val_diff = self.max_pressure - self.min_pressure

        # Kreslení
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(0, 0, 480, 480)

        # Kreslení čárek - výpočet
        painter.translate(240, 240)
        painter.rotate(180 - 45)
        painter.setPen(QPen(QColor(0, 0, 0), 4))
        painter.setBrush(QBrush(QColor(0, 0, 0)))

        painter.save()

        large_tick_count = 15
        large_tick_size = 40
        small_ticks_count = 4
        small_tick_size = 20

        val_per_large_tick = int(val_diff / (large_tick_count-1))
        font_size = 30

        font = QFont("DIN 1451")
        font.setPixelSize(font_size)

        painter.setFont(font)

        # Velké čárky
        for i in range(large_tick_count):
            if i % 2 == 1:
                # Ano vím je zde hodně magických čísel
                # Takhle to ale vypadá nejlépe
                # Ta -30 se ale musí přenastavit podle font_size, vše ostatní se nastaví samo
                # V tomto čísle jsem žádný vztah nenašel bohužel
                painter.save()
                painter.translate(240 - (font_size * 2)-20, 0)
                if i == 1 or i == large_tick_count-2:
                    painter.rotate(270)
                else:
                    painter.rotate(90)
                text = str(self.min_pressure + 10 * i)
                painter.drawText(-(len(text)*(font_size/3.5)), 0, str(self.min_pressure + val_per_large_tick*i))
                painter.restore()

            painter.drawLine(240-large_tick_size, 0, 240, 0)
            painter.rotate(270/(large_tick_count-1))


        painter.restore()
        painter.save()

        # Malé čárky
        for i in range((large_tick_count-1) * (small_ticks_count+1)):
            if i % (small_ticks_count + 1) != 0:
                painter.drawLine(240 - small_tick_size, 0, 240, 0)

            painter.rotate(270/((large_tick_count-1)*(small_ticks_count+1)))

        painter.restore()

        painter.resetTransform()
        painter.translate(240, 240)

        # Nápis textu
        font.setPixelSize(20)
        painter.setFont(font)
        metrics = QFontMetrics(painter.font())
        rect = metrics.boundingRect("BAROMETER")
        painter.drawText(-rect.width()/2, 200, "BAROMETER")

        rect = metrics.boundingRect("hPa")
        painter.drawText(-rect.width()/2, 220, "hPa")

        # Ručička
        painter.rotate(180-45)
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(-20, -20, 40, 40)

        # Zjištění úhlu
        # Snapni hodnotu, pokud je mimo rozsah
        if press < self.min_pressure:
            press = self.min_pressure
        elif press > self.max_pressure:
            press = self.max_pressure

        press_helper = press-self.min_pressure

        deg_per_val = 270/val_diff
        result = press_helper*deg_per_val

        painter.rotate(result)
        painter.drawRect(-100, -5, 300, 10)

        

