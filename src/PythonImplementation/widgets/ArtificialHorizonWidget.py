from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QTransform, QFontDatabase, QPen, QColor
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
import math

from sensors.MMA8452Q import MMA8452Q


class ArtificialHorizonMovingPart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.pitch = 0
        self.roll = 0

        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def setPitch(self, deg):
        self.pitch = deg
        self.update()

    def setRoll(self, deg):
        self.roll = deg
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pixels_per_degree = 6

        w = self.width()
        h = self.height()
        cx, cy = w / 2, h / 2

        painter.translate(cx, cy)
        painter.rotate(-self.roll)
        painter.translate(0, self.pitch * pixels_per_degree)

        # sky and ground
        sky = QColor("#5b93c5")
        ground = QColor("#7d5233")
        rect_big = QRectF(-1000, -1000, 2000, 2000)

        painter.fillRect(QRectF(rect_big.left(), rect_big.top(),
                                rect_big.width(), rect_big.height() / 2),
                         sky)

        painter.fillRect(QRectF(rect_big.left(),
                                rect_big.top() + rect_big.height() / 2,
                                rect_big.width(), rect_big.height() / 2),
                         ground)

        # horizon line
        pen = QPen(Qt.white, 6)
        painter.setPen(pen)
        painter.drawLine(-500, 0, 500, 0)

        # ----- Pitch Ladder -----
        painter.setPen(QPen(Qt.white, 3))

        pitch_step = 5  # draw mark every 5 degrees

        for deg in range(-60, 61, pitch_step):
            if deg == 0:
                continue  # skip horizon; drawn separately

            # y-position *in the transformed coordinate system*
            y = -deg * pixels_per_degree

            # line length
            if deg % 10 == 0:
                length = 120  # longer major ticks
            else:
                length = 60  # minor ticks

            # draw the ladder line
            painter.drawLine(-length / 2, y, length / 2, y)

            # draw text label (only for major ticks)
            if deg % 10 == 0:
                painter.setPen(Qt.white)
                painter.drawText(-length / 2 - 35, y + 5, f"{deg}")
                painter.drawText(length / 2 + 10, y + 5, f"{deg}")


class HorizonForeground(QWidget):
    def __init__(self, surround_pix, parent=None):
        super().__init__(parent)
        self.surround = surround_pix

    def paintEvent(self, event):
        painter = QPainter(self)



        painter.drawPixmap(0, 0, self.surround)

        w = self.width()
        h = self.height()
        cx, cy = w / 2, h / 2

        painter.setPen(QPen(Qt.white, 2))

        diameter = 350
        w = self.width()
        h = self.height()

        # Calculate top-left corner so the circle is centered
        x = (w - diameter) / 2
        y = (h - diameter) / 2

        painter.drawEllipse(x, y, diameter, diameter)

        # fixed reticle
        painter.drawLine(cx - 100, cy, cx - 30, cy)
        painter.drawLine(cx - 30, cy, cx - 30, cy + 20)

        painter.drawLine(cx + 100, cy, cx + 30, cy)
        painter.drawLine(cx + 30, cy, cx + 30, cy + 20)



class ArtificialHorizonWidget(QWidget):
    def __init__(self, is_raspberry_pi = False):
        super().__init__()
        self.sensor = None
        self.is_raspberry_pi = is_raspberry_pi

        self.surround_pix = QPixmap("assets/artificial-horizon-surroundings.png") \
                                .scaled(480, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # bottom layer (moving)
        self.moving = ArtificialHorizonMovingPart(self)
        self.moving.setGeometry(0, 0, 480, 480)

        # top layer (surround image + fixed marks)
        self.foreground = HorizonForeground(self.surround_pix, self)
        self.foreground.setGeometry(0, 0, 480, 480)

        # ensure correct stacking
        self.moving.lower()      # bottom
        self.foreground.raise_() # top

        # test animation
        self.roll, self.pitch = 0, 0
        from PySide6.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        if not self.is_raspberry_pi:
            return

        if self.sensor is None:
            if MMA8452Q.detect(11) is None:
                print("Trying to find SHT3x. Found nothing.")
                return
            self.sensor = MMA8452Q(11)

        try:
            roll, pitch = self.sensor.read_gyro()
            self.pitch = pitch
            self.roll = roll
            self.moving.setRoll(self.roll)
            self.moving.setPitch(self.pitch)
        except:
            print("Reading from sensor failed. Will try to reconnect again next time.")
            self.sensor = None
            pass


