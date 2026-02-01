from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QStackedLayout, \
    QLabel, QGridLayout, QSizePolicy
from PySide6.QtCore import Qt

from networking.TcpClient import TcpClient
from networking.CommandTypes import *

class ClientWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ip_input = None
        self.tcp_client = None

        self.setFixedSize(300, 50)

        # Okno se skládá ze dvou režimů: Připojení a samotný panel
        # Stacked layout mezi něma přepíná

        self.stacked = QStackedLayout(self)

        self.connect_widget = self._build_connect_widget()
        self.panel_widget = self._build_panel_widget()

        self.stacked.addWidget(self.connect_widget)
        self.stacked.addWidget(self.panel_widget)

        self.stacked.setCurrentWidget(self.connect_widget)


    def _build_connect_widget(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP Adresa")

        connect_btn = QPushButton("Připojit")
        connect_btn.clicked.connect(self.on_button_clicked)

        layout.addWidget(self.ip_input)
        layout.addWidget(connect_btn)

        return widget

    def _build_panel_widget(self):
        widget = QWidget()

        main_layout = QVBoxLayout(widget)
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

        return widget


    def on_button_clicked(self):
        ip = self.ip_input.text()

        # Ověření vstupu
        # Je-li nalezen problém, vykresli chybu a ukonči funkci předčasně
        split = ip.split(".")
        if len(split) == 4:
            for i in split:
                if not i.isnumeric():
                    QMessageBox.critical(self, "Error", "IP adresa se skládá ze 4 čísel od 0 do 255")
                    return
                else:
                    val = int(i)
                    if val < 0 or val > 255:
                        QMessageBox.critical(self, "Error", "IP adresa obsahuje pouze čísla od 0 do 255")
                        return

        else:
            QMessageBox.critical(self, "Error", "Neplatná IP adresa.")

        self.tcp_client = TcpClient(ip, 5000)
        self.tcp_client.error.connect(self.on_connection_error)
        self.tcp_client.connected.connect(self.on_connection_success)
        self.tcp_client.disconnected.connect(self.on_connection_closed)

        self.tcp_client.start()

    def on_connection_error(self):
        QMessageBox.critical(self, "Error", "Připojení selhalo")

    def on_connection_success(self):
        #QMessageBox.information(self, "Úspěch", "Připojení bylo úspěšné")
        self.stacked.setCurrentWidget(self.panel_widget)
        self.setFixedSize(400, 600)

    def on_connection_closed(self):
        self.stacked.setCurrentWidget(self.connect_widget)
        self.setFixedSize(300, 50)

    def closeEvent(self, event):
        if self.tcp_client is None:
            return

        self.tcp_client.stop()
        event.accept()


    # KOMUNIKACE PŘES TCP
    # Zde se nacházejí všechny instrukce, které je tento klient schopný poslat

    def send_shutdown_command(self):
        self.tcp_client.send_command(SHUTDOWN_DTO)

    def send_shutdown_debug_command(self):
        self.tcp_client.send_command(SHUTDOWN_DEBUG_DTO)

    def send_default_window_command(self):
        self.tcp_client.send_command(ENTER_DEFAULT_WINDOW_DTO)

    def send_manual_window_command(self):
        self.tcp_client.send_command(ENTER_MANUAL_WINDOW_DTO)

    def send_set_clock_style_analog_command(self):
        self.tcp_client.send_command(DISPLAY_CLOCK_DTO)
        self.tcp_client.send_command(CHANGE_CLOCK_STYLE_ANALOG_DTO)

    def send_set_clock_style_digital_a_command(self):
        self.tcp_client.send_command(DISPLAY_CLOCK_DTO)
        self.tcp_client.send_command(CHANGE_CLOCK_STYLE_DIGITAL_A_DTO)

    def send_set_weather_station_digital_command(self):
        self.tcp_client.send_command(DISPLAY_WEATHER_STATION_DTO)

    def send_set_accelerometer_artificial_horizon_command(self):
        self.tcp_client.send_command(DISPLAY_ARTIFICIAL_HORIZON_DTO)
