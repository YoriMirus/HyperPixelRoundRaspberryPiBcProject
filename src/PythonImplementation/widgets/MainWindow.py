from networking.TcpListener import TcpListener
from networking.CommandDTO import CommandDTO

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QEvent, QTimer,QCoreApplication

from helpers.SensorManager import SensorManager
from widgets.Layouts.SlidingLayout import SlidingLayout


class MainWindow(QWidget):
    def __init__(self, is_raspberry_pi=False):
        super().__init__()

        if is_raspberry_pi:
            # Ano některé parametry zde nedávají moc smysl
            # Z nějakého důvodu čistý fullscreen je trošičku mimo od prostředku
            # move by prý měl vypnout fullScreen ale bez FullScreen tento fix nefunguje
            # setFixedSize jenom vypíná window resizing, protože i fullscreen aplikace evidentně jde resizovat z nějakého záhadného důvodu
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self.setWindowFlag(Qt.CustomizeWindowHint)
            self.showFullScreen()
            self.move(0,7)

        self.sensorManager = SensorManager()

        self.setStyleSheet("background-color: black")

        layout = QVBoxLayout()
        layout.addWidget(SlidingLayout(is_raspberry_pi=is_raspberry_pi, sensorManager=self.sensorManager))
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
