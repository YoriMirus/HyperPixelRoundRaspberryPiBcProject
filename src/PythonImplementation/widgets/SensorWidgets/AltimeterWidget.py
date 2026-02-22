from math import cos, sin, radians

from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QBrush, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout

class AltimeterWidget(QWidget):
    def __init__(self, parent=None):
        super(AltimeterWidget, self).__init__(parent)

        self.setFixedSize(480,480)

    def paintEvent(self, event, /):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(QColor("white")))

        # Nastav koordinaci 0, 0 na prostředek widgetu
        painter.translate(240, 240)

        drawAltimeterBackground(painter)
        drawHundrethsHand(painter)
        drawThousandthHand(painter)
        drawTenThousandthHand(painter)
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
            x - width / 2,
            y + (ascent - descent) / 2,
            text
        )

        #painter.drawEllipse(-125, -125, 250, 250)
        #painter.drawEllipse(-240, -240, 480, 480)

def drawHundrethsHand(painter: QPainter):
    painter.save()
    painter.setBrush(QBrush(QColor("white")))
    painter.setPen(QPen(QColor("black"), 2))

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

def drawThousandthHand(painter: QPainter):
    painter.save()
    painter.rotate(90)

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

def drawTenThousandthHand(painter: QPainter):
    painter.save()
    painter.rotate(120)

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
