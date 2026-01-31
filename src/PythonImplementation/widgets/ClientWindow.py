from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit, QMessageBox, QStackedLayout
from PySide6.QtCore import Qt

from networking.TcpClient import TcpClient
from networking.CommandTypes import *

class ClientWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ip_input = None
        self.tcp_client = None


        self.setFixedSize(300, 50)

        # 🔹 stacked layout owns the whole window
        self.stacked = QStackedLayout(self)

        # build both screens once
        self.connect_widget = self._build_connect_widget()
        self.panel_widget = self._build_panel_widget()

        self.stacked.addWidget(self.connect_widget)
        self.stacked.addWidget(self.panel_widget)

        # show connect screen initially
        self.stacked.setCurrentWidget(self.connect_widget)


    def _build_connect_widget(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP Address")

        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.on_button_clicked)

        layout.addWidget(self.ip_input)
        layout.addWidget(connect_btn)

        return widget

    def _build_panel_widget(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        shutdown_btn = QPushButton("Shutdown")
        shutdown_btn.clicked.connect(self.send_shutdown_command)
        debug_btn = QPushButton("Enter debug mode")
        debug_btn.clicked.connect(self.send_shutdown_debug_command)

        layout.addWidget(shutdown_btn)
        layout.addWidget(debug_btn)

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
        #self.tcp_client.connected.connect(lambda: self.label.setText("Connected"))
        #self.tcp_client.disconnected.connect(lambda: self.label.setText("Disconnected"))
        self.tcp_client.error.connect(self.on_connection_error)
        self.tcp_client.connected.connect(self.on_connection_success)

        self.tcp_client.start()

    def on_connection_error(self):
        QMessageBox.critical(self, "Error", "Připojení selhalo")

    def on_connection_success(self):
        #QMessageBox.information(self, "Úspěch", "Připojení bylo úspěšné")
        self.stacked.setCurrentWidget(self.panel_widget)

    def on_connection_closed(self):
        self.stacked.setCurrentWidget(self.connect_widget)

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

