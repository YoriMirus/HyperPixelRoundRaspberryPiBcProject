from networking.CommandTypes import create_status_dto
from networking.TcpListener import TcpListener
from networking.CommandDTO import CommandDTO

from PySide6.QtWidgets import QWidget, QStackedLayout
from PySide6.QtCore import Qt, QTimer,QCoreApplication

from helpers.SensorManager import SensorManager
from helpers.BrightnessController import BrightnessController
from sensors.VirtualBarometer import VirtualBarometer
from sensors.VirtualTemperatureSensor import VirtualTemperatureSensor
from widgets.Layouts.ManualModeLayout import ManualModeLayout
from widgets.Layouts.SlidingLayout import SlidingLayout

from sensors.VirtualAccelerometer import VirtualAccelerometer

import json

from dataclasses import asdict

class MainWindow(QWidget):
    def __init__(self, is_raspberry_pi=False):
        super().__init__()
        self.is_raspberry_pi = is_raspberry_pi

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

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

        self.sliding_layout = SlidingLayout(is_raspberry_pi=is_raspberry_pi, sensorManager=self.sensorManager)

        self.stacked = QStackedLayout()
        self.stacked.addWidget(self.sliding_layout)
        self.stacked.setCurrentWidget(self.sliding_layout)
        self.setLayout(self.stacked)

        # Časovač pro kontrolu senzorů
        self.timer = QTimer()
        self.timer.timeout.connect(self.checkForSensors)
        self.timer.start(1000)

        if is_raspberry_pi:
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
        elif command.name == "change_display":
            index = command.args[0]
            if index.isnumeric():
                index_int = int(index)
                self.sliding_layout.animate_to(index_int)
            else:
                print(f"{command.ip} is requesting {command.name} with args {command.args}")
                print("Invalid index. Doing nothing.")
        elif command.name == "change_display_style":
            index_1 = command.args[0]
            index_2 = command.args[1]
            if index_1.isnumeric() and index_2.isnumeric():
                display_index_int = int(index_1)
                style_index_int = int(index_2)
                self.sliding_layout.change_display_style(display_index_int, style_index_int)
                self.sliding_layout.animate_to(display_index_int)

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
        elif command.name == "calibrate_gyro_level":
            if self.is_raspberry_pi:
                if self.sensorManager.MMA8452Q is not None:
                    self.sensorManager.MMA8452Q.calibrate_level()
                else:
                    print(f"{command.ip} is requesting {command.name} with args {command.args}")
                    print("MMA8452Q is not connected. Doing nothing.")
            else:
                print(f"{command.ip} is requesting {command.name} with args {command.args}")
                print("This isn't a raspberry pi. No sensor present here.")
        elif command.name == "calibrate_gyro_artificial_horizon":
            if self.is_raspberry_pi:
                if self.sensorManager.MMA8452Q is not None:
                    self.sensorManager.MMA8452Q.calibrate_artificial_horizon()
                else:
                    print(f"{command.ip} is requesting {command.name} with args {command.args}")
                    print("MMA8452Q is not connected. Doing nothing.")
            else:
                print(f"{command.ip} is requesting {command.name} with args {command.args}")
                print("This isn't a raspberry pi. No sensor present here.")
        elif command.name == "set_virtual_gyro_value":
            roll = float(command.args[0])
            pitch = float(command.args[1])
            if not self.is_raspberry_pi:
                self.sensorManager.MMA8452Q.set_gyro(roll, pitch)
        elif command.name == "set_virtual_barometer_altitude":
            altitude = int(command.args[0])
            if not self.is_raspberry_pi:
                self.sensorManager.Bmp180.set_altitude(altitude)
        else:
            print(f"{command.ip} is requesting {command.name} with args {command.args}")
            print("I have no idea what that means. Doing nothing.")

    def closeEvent(self, event):
        self.listener.stop()
        if self.is_raspberry_pi:
            self.brightness_controller.shutdown()
        event.accept()

    def checkForSensors(self):
        if not self.is_raspberry_pi and self.sensorManager.MMA8452Q is None:
            self.sensorManager.MMA8452Q = VirtualAccelerometer()

        if not self.is_raspberry_pi and self.sensorManager.SHT3x is None:
            self.sensorManager.SHT3x = VirtualTemperatureSensor()

        if not self.is_raspberry_pi and self.sensorManager.Bmp180 is None:
            self.sensorManager.Bmp180 = VirtualBarometer()

        self.sensorManager.CheckForSensors()
