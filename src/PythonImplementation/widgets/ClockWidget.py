from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget, QFrame, QLabel
from PySide6.QtGui import QPixmap, QPainter, QTransform, QFontDatabase
from PySide6.QtCore import Qt, QTimer

class ClockHandsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(480,480)

        self.hour_pix = QPixmap("assets/hour-hand.png")
        self.minute_pix = QPixmap("assets/minute-hand.png")
        self.second_pix = QPixmap("assets/second-hand.png")


    def paintEvent(self, event):
        p = QPainter(self)

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

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.clock_hands_layer = ClockHandsWidget(self)

        self.setStyleSheet("QWidget { background-color: black; }")
        self.bg = QPixmap("assets/clock.png").scaled(480, 480,
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.date_time_frame = QFrame(self)
        self.date_time_frame.setGeometry(120, 290, 240, 60)
        self.date_time_frame.setStyleSheet("border: 2px solid white;")

        self.date_time_label = QLabel(self.date_time_frame)
        self.date_time_label.setFont(QFontDatabase.font("Saira Stencil One", "", 30))
        self.date_time_label.setStyleSheet("border: none; background-color: transparent;")
        self.date_time_label.setGeometry(0, 0, self.date_time_frame.width(), self.date_time_frame.height())
        self.date_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.clock_hands_layer.raise_()

        # redraw approximately once per second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.update()

    def paintEvent(self, event):
        now = datetime.now()

        CZECH_WEEKDAYS = {
            0: "PO",  # Monday
            1: "ÚT",  # Tuesday
            2: "ST",  # Wednesday
            3: "ČT",  # Thursday
            4: "PÁ",  # Friday
            5: "SO",  # Saturday
            6: "NE",  # Sunday
        }

        weekday_cz = CZECH_WEEKDAYS[now.weekday()]
        self.date_time_label.setText(weekday_cz + " " + now.strftime("%d.%m") + "." + now.strftime("%Y")[2:])

        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.drawPixmap(0, 0, self.bg)
        self.clock_hands_layer.update()

