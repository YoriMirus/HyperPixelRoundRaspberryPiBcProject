from networking.TcpListener import TcpListener
from networking.CommandDTO import CommandDTO

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QEvent, QTimer,QCoreApplication

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

        self.listener = TcpListener()
        self.listener.command_received.connect(self.on_command_received)
        self.listener.start()

    def on_command_received(self, command: CommandDTO):
        print(f"{command.ip} is requesting {command.name} with args {command.args}")

        if command.name == "shutdown":
            self.listener.stop()
            self.listener.wait()
            QCoreApplication.exit(0)
        elif command.name == "shutdown_debug":
            self.listener.stop()
            self.listener.wait()
            # Jakékoliv číslo jiné než 0 je v run.sh skriptu na raspberry pi vnímáno jako error a samotný OS se nevypne
            # Hodí se pro debug účely kdy je potřeba vypnout program, ale nevypnout samotné raspberry pi
            QCoreApplication.exit(2)
        else:
            print("I have no idea what that means. Doing nothing.")

    def closeEvent(self, event):
        self.listener.stop()
        event.accept()

    def checkForSensors(self):
        self.sensorManager.CheckForSensors()
