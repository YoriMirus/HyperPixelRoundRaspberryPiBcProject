from math import cos, sin, radians

from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QBrush, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout

from helpers.SensorManager import SensorManager


class AltimeterWidget(QWidget):
    def __init__(self, sensorManager: SensorManager = None, parent=None):
        super(AltimeterWidget, self).__init__(parent)

        self.sensorManager = sensorManager

        self.setFixedSize(480,480)
        self.altitude = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

    def onTimerTick(self):
        if self.sensorManager.Bmp180 is None:
            return

        alt = self.sensorManager.Bmp180.get_altitude()
        # Převeď na ft
        alt_feet = alt * 3.2808399
        self.altitude = alt_feet

        self.update()

    def paintEvent(self, event, /):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(QColor("white")))

        # Nastav koordinaci 0, 0 na prostředek widgetu
        painter.translate(240, 240)

        drawAltimeterBackground(painter)
        drawUnitsText(painter)
        drawHundrethsHand(painter, self.altitude)
        drawThousandthHand(painter, self.altitude)
        drawTenThousandthHand(painter, self.altitude)
        drawCenterCircles(painter)



def drawAltimeterBackground(painter: QPainter):
    angle_offset = radians(90)

    digits_on_display = 10
    ticks_per_digit = 4

    # Velké čárky
    major_pen = QPen(QColor("white"))
    major_pen.setCapStyle(Qt.RoundCap)
    major_pen.setWidth(4)
    painter.setPen(major_pen)
    for i in range(digits_on_display):
        angle = radians(i * (360 / digits_on_display)) - angle_offset

        x_start = (cos(angle) * 240)
        y_start = (sin(angle) * 240)

        x_end = (cos(angle) * 200)
        y_end = (sin(angle) * 200)

        painter.drawLine(int(x_start), int(y_start), int(x_end), int(y_end))

    # Malé čárky
    minor_pen = QPen(QColor("white"))
    minor_pen.setCapStyle(Qt.RoundCap)
    minor_pen.setWidth(2)
    painter.setPen(minor_pen)
    small_tick_count = (ticks_per_digit + 1) * digits_on_display
    for i in range(small_tick_count):
        if i % (ticks_per_digit + 1) == 0:
            continue

        angle = radians(i * (360 / small_tick_count)) - angle_offset

        x_start = (cos(angle) * 240)
        y_start = (sin(angle) * 240)

        x_end = (cos(angle) * 220)
        y_end = (sin(angle) * 220)

        painter.drawLine(int(x_start), int(y_start), int(x_end), int(y_end))

    digits_on_display = 10
    radius_text = 170

    font = QFont("Arial", 42)
    painter.setFont(font)

    metrics = QFontMetrics(font)

    for i in range(digits_on_display):
        angle = radians(i * (360 / digits_on_display)) - angle_offset

        x = cos(angle) * radius_text
        y = sin(angle) * radius_text

        text = str(i)

        width = metrics.horizontalAdvance(text)
        ascent = metrics.ascent()
        descent = metrics.descent()

        painter.drawText(
            int(x - width / 2),
            int(y + (ascent - descent) / 2),
            text
        )

def drawUnitsText(painter: QPainter):
    painter.save()

    font = QFont("Arial", 32)
    font.setBold(True)
    painter.setFont(font)

    painter.setPen(QPen(QColor("white")))

    text = "Ft"
    metrics = QFontMetrics(font)

    width = metrics.horizontalAdvance(text)
    ascent = metrics.ascent()
    descent = metrics.descent()

    x = -width / 2
    y = -110 + (ascent - descent) / 2

    painter.drawText(int(x), int(y), text)

    text = "ALT"
    metrics = QFontMetrics(font)

    width = metrics.horizontalAdvance(text)
    ascent = metrics.ascent()
    descent = metrics.descent()

    # Center horizontally
    x = -width / 2

    # Position below hands but above bottom digit
    y = 110 + (ascent - descent) / 2

    painter.drawText(int(x), int(y), text)

    painter.restore()

def drawHundrethsHand(painter: QPainter, altitude: int):
    painter.save()
    painter.setBrush(QBrush(QColor("white")))
    painter.setPen(QPen(QColor("black"), 2))

    angle = ((altitude % 1000)/1000) * 360
    painter.rotate(angle - 90)

    # Ručička je 200 pixelů široká v ukazujícím směru
    # Pro symetrii udělejme ji 100 px širokou v opačném

    painter.drawPolygon([
        QPoint(0, -10),
        QPoint(200, -10),
        QPoint(220, 0),
        QPoint(200, 10),
        QPoint(0, 10)
    ])

    painter.setBrush(QBrush(QColor("black")))
    painter.setPen(QPen(QColor("white")))

    painter.drawRect(-100, -10, 100, 20)
    painter.drawEllipse(-115, -15, 30, 30)

    painter.restore()

def drawThousandthHand(painter: QPainter, altitude: int):
    painter.save()

    angle = ((altitude % 10000)/10000) * 360
    painter.rotate(angle - 90)

    painter.setPen(QPen(QColor("black"), 2))
    painter.setBrush(QBrush(QColor("white")))

    painter.drawPolygon([
        QPoint(0, -10),
        QPoint(1, 10),
        QPoint(67, 15),
        QPoint(125, 0),
        QPoint(67, -15)
    ])

    painter.setPen(QPen(QColor("white")))
    painter.setBrush(Qt.NoBrush)

    paths = QPainterPath()
    paths.moveTo(0, 5)
    paths.lineTo(-67, 20)
    paths.quadTo(-77, 0, -67, -20)
    paths.lineTo(0, -5)
    painter.drawPath(paths)

    painter.restore()

def drawTenThousandthHand(painter: QPainter, altitude: int):
    painter.save()

    angle = ((altitude % 100000)/100000) * 360
    painter.rotate(angle - 90)

    painter.setPen(QPen(QColor("black"), 2))
    painter.setBrush(QBrush(QColor("white")))
    painter.drawPolygon([
        QPoint(0, 5),
        QPoint(110, 5),
        QPoint(125, 0),
        QPoint(110, -5),
        QPoint(0, -5)
    ])
    painter.restore()

def drawCenterCircles(painter: QPainter):
    painter.save()
    painter.setBrush(QBrush(QColor("black")))
    painter.setPen(QPen(QColor("white")))

    painter.drawEllipse(-20, -20, 40, 40)
    painter.drawEllipse(-15, -15, 30, 30)
    painter.restore()
