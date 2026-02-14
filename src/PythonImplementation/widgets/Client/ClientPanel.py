from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, Signal

from networking.CommandTypes import *

class ClientPanel(QWidget):
    on_command_send_request = Signal(object)
    def __init__(self, parent=None):
        super(ClientPanel, self).__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10,10,10,10)

        # Tlačítka pro vypnutí programu
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        shutdown_btn = QPushButton("Vypnout raspberry pi")
        shutdown_btn.clicked.connect(self.send_shutdown_command)
        debug_btn = QPushButton("Ukončit program")
        debug_btn.clicked.connect(self.send_shutdown_debug_command)
        layout.addWidget(shutdown_btn)
        layout.addWidget(debug_btn)

        main_layout.addLayout(layout)

        # Styl vykreslování label
        render_style_lbl = QLabel("Styl vykreslování")
        render_style_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(render_style_lbl)

        # Režim vykreslování
        layout = QHBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(10)

        default_btn = QPushButton("Výchozí režim")
        default_btn.clicked.connect(self.send_default_window_command)
        manual_btn = QPushButton("Manuální režim")
        manual_btn.clicked.connect(self.send_manual_window_command)
        layout.addWidget(default_btn)
        layout.addWidget(manual_btn)

        main_layout.addLayout(layout)

        # Nastavení stylů stránek
        page_style_grid = QGridLayout()

        page_style_grid.addWidget(QLabel("Hodiny"), 0, 0)
        page_style_grid.addWidget(QLabel("Meteostanice"), 1, 0)
        page_style_grid.addWidget(QLabel("Akcelerometr"), 2, 0)

        btn = QPushButton("Klasické")
        btn.clicked.connect(self.send_set_clock_style_analog_command)
        page_style_grid.addWidget(btn, 0, 1)

        btn = QPushButton("Digitální")
        btn.clicked.connect(self.send_set_clock_style_digital_a_command)
        page_style_grid.addWidget(btn, 0, 2)

        page_style_grid.addWidget(QPushButton("Digitální 2"), 0, 3)

        btn = QPushButton("Digitální")
        btn.clicked.connect(self.send_set_weather_station_digital_command)
        page_style_grid.addWidget(btn, 1, 1)

        btn = QPushButton("Umělý horizont")
        btn.clicked.connect(self.send_set_accelerometer_artificial_horizon_command)
        page_style_grid.addWidget(btn, 2, 1)

        main_layout.addLayout(page_style_grid)

        filler_label = QLabel("")
        filler_label.setStyleSheet("background-color: transparent")
        filler_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout.addWidget(filler_label)

# KOMUNIKACE PŘES TCP
    # Zde se nacházejí všechny instrukce, které je tento klient schopný poslat

    def send_shutdown_command(self):
        self.on_command_send_request.emit(SHUTDOWN_DTO)

    def send_shutdown_debug_command(self):
        self.on_command_send_request.emit(SHUTDOWN_DEBUG_DTO)

    def send_default_window_command(self):
        self.on_command_send_request.emit(ENTER_DEFAULT_WINDOW_DTO)

    def send_manual_window_command(self):
        self.on_command_send_request.emit(ENTER_MANUAL_WINDOW_DTO)

    def send_set_clock_style_analog_command(self):
        self.on_command_send_request.emit(DISPLAY_CLOCK_DTO)
        self.on_command_send_request.emit(CHANGE_CLOCK_STYLE_ANALOG_DTO)

    def send_set_clock_style_digital_a_command(self):
        self.on_command_send_request.emit(DISPLAY_CLOCK_DTO)
        self.on_command_send_request.emit(CHANGE_CLOCK_STYLE_DIGITAL_A_DTO)

    def send_set_weather_station_digital_command(self):
        self.on_command_send_request.emit(DISPLAY_WEATHER_STATION_DTO)

    def send_set_accelerometer_artificial_horizon_command(self):
        self.on_command_send_request.emit(DISPLAY_ARTIFICIAL_HORIZON_DTO)

