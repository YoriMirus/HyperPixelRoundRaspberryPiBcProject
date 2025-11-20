from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPixmap, QPainter, QTransform
from PySide6.QtCore import Qt, QTimer

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480, 480)
        self.setStyleSheet("QWidget { background-color: black; }")
        self.bg = QPixmap("assets/clock.png").scaled(480, 480,
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.hour_pix = QPixmap("assets/hour-hand.png")
        self.minute_pix = QPixmap("assets/minute-hand.png")
        self.second_pix = QPixmap("assets/second-hand.png")
        # redraw approximately once per second (use shorter for smooth)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.drawPixmap(0, 0, self.bg)

        now = datetime.now()
        hour_angle = (now.hour % 12 + now.minute / 60.0) * 30.0
        minute_angle = (now.minute + now.second / 60.0) * 6.0
        second_angle = now.second * 6.0

        cx, cy = 240, 240

        hour_transform = QTransform()
        hour_transform.translate(cx, cy)
        hour_transform.rotate(hour_angle)
        hour_transform.translate(-self.hour_pix.width() / 2, -self.hour_pix.height() / 2)

        minute_transform = QTransform()
        minute_transform.translate(cx, cy)
        minute_transform.rotate(minute_angle)
        minute_transform.translate(-self.minute_pix.width() / 2, -self.minute_pix.height() / 2)

        second_transform = QTransform()
        second_transform.translate(cx, cy)
        second_transform.rotate(second_angle)
        second_transform.translate(-self.second_pix.width() / 2, -self.second_pix.height() / 2)

        p.setTransform(hour_transform)
        p.drawPixmap(0,0, self.hour_pix)

        p.setTransform(second_transform)
        p.drawPixmap(0,0, self.second_pix)

        p.setTransform(minute_transform)
        p.drawPixmap(0,0, self.minute_pix)