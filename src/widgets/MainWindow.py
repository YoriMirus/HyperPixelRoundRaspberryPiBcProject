from networking.CommandTypes import create_status_dto
from networking.TcpListener import TcpListener
from networking.CommandDTO import CommandDTO

from PySide6.QtWidgets import QWidget, QStackedLayout
from PySide6.QtCore import Qt, QTimer,QCoreApplication

from helpers.SensorManager import SensorManager
from helpers.BrightnessController import BrightnessController
from widgets.Layouts.ManualModeLayout import ManualModeLayout
from widgets.Layouts.SlidingLayout import SlidingLayout

import json

from dataclasses import asdict

class MainWindow(QWidget):
    def __init__(self, is_raspberry_pi=False):
        super().__init__()
        self.is_raspberry_pi = is_raspberry_pi

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
        self.brightness_controller = None

        self.manual_mode = False
        self.sliding_layout = SlidingLayout(is_raspberry_pi=is_raspberry_pi, sensorManager=self.sensorManager)
        self.manual_mode_layout = ManualModeLayout(self.sensorManager)

        self.stacked = QStackedLayout()
        self.stacked.addWidget(self.sliding_layout)
        self.stacked.addWidget(self.manual_mode_layout)
        self.stacked.setCurrentWidget(self.sliding_layout)
        self.setLayout(self.stacked)

        # Časovač pro kontrolu senzorů
        if is_raspberry_pi:
            self.timer = QTimer()
            self.timer.timeout.connect(self.checkForSensors)
            self.timer.start(1000)
            self.brightness_controller = BrightnessController()


        self.listener = TcpListener()
        self.listener.command_received.connect(self.on_command_received)
        self.listener.start()

    def on_command_received(self, command: CommandDTO):
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
        elif command.name == "enter_default_window":
            self.stacked.setCurrentWidget(self.sliding_layout)
        elif command.name == "enter_manual_window":
            self.stacked.setCurrentWidget(self.manual_mode_layout)
        elif command.name == "change_display":
            index = command.args[0]
            if index.isnumeric():
                index_int = int(index)
                self.manual_mode_layout.setDisplayedWidget(index_int)
            else:
                print(f"{command.ip} is requesting {command.name} with args {command.args}")
                print("Invalid index. Doing nothing.")
        elif command.name == "change_clock_style":
            index = command.args[0]
            if index.isnumeric():
                index_int = int(index)
                self.manual_mode_layout.changeWidgetStyle(0, index_int)
            else:
                print(f"{command.ip} is requesting {command.name} with args {command.args}")
                print("Invalid index. Doing nothing.")
        elif command.name == "get_status":
            status = self.sensorManager.get_sensor_status()
            # status je DataClass, musíme ho převést na Dictionary, aby json věděl, co s tím má dělat
            self.listener.send_command(create_status_dto(json.dumps(asdict(status))))
        elif command.name == "change_brightness":
            value = int(command.args[0])
            if self.is_raspberry_pi:
                self.brightness_controller.set_brightness_percent(value)
            else:
                print(f"{command.ip} is requesting {command.name} with args {command.args}")
                print("This isn't a raspberry pi. No brightness controls available here.")
        else:
            print(f"{command.ip} is requesting {command.name} with args {command.args}")
            print("I have no idea what that means. Doing nothing.")

    def closeEvent(self, event):
        self.listener.stop()
        if self.is_raspberry_pi:
            self.brightness_controller.shutdown()
        event.accept()

    def checkForSensors(self):
        self.sensorManager.CheckForSensors()
