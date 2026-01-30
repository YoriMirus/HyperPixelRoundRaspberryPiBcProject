from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QEvent, QTimer

from helpers.SensorManager import SensorManager
from widgets.DefaultWindow import DefaultWindow


class MainWindow(QWidget):
    def __init__(self, is_raspberry_pi=False):
        super().__init__()
        self.sensorManager = SensorManager()

        self.setStyleSheet("background-color: black")

        layout = QVBoxLayout()
        layout.addWidget(DefaultWindow(is_raspberry_pi=is_raspberry_pi, sensorManager=self.sensorManager))
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        # Časovač pro kontrolu senzorů
        if is_raspberry_pi:
            self.timer = QTimer()
            self.timer.timeout.connect(self.checkForSensors)
            self.timer.start(1000)

    def checkForSensors(self):
        self.sensorManager.CheckForSensors()
