from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QMessageBox, QStackedLayout

from networking.TcpClient import TcpClient
from networking.GetStatusDTO import *

from widgets.Client.ConnectionWidget import ConnectionWidget
from widgets.Client.ClientPanel import ClientPanel

import json

class ClientWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ip_input = None
        self.tcp_client = None

        self.setFixedSize(300, 50)

        # Okno se skládá ze dvou režimů: Připojení a samotný panel
        # Stacked layout mezi něma přepíná

        self.stacked = QStackedLayout(self)

        self.connect_widget = ConnectionWidget()
        self.connect_widget.on_connection_attempt.connect(self.on_connection_attempt)
        self.panel_widget = ClientPanel()
        self.panel_widget.on_command_send_request.connect(self.on_command_send_request)

        self.stacked.addWidget(self.connect_widget)
        self.stacked.addWidget(self.panel_widget)

        self.stacked.setCurrentWidget(self.connect_widget)


    def on_connection_attempt(self, ip):
        if self.tcp_client is not None:
            self.tcp_client.stop()
            self.tcp_client.deleteLater()
            self.tcp_client = None

        self.tcp_client = TcpClient(ip, 5000)
        self.tcp_client.error.connect(self.on_connection_error)
        self.tcp_client.connected.connect(self.on_connection_success)
        self.tcp_client.disconnected.connect(self.on_connection_closed)
        self.tcp_client.command_received.connect(self.on_data_received)

        self.tcp_client.start()
    def on_command_send_request(self, DTO):
        self.tcp_client.send_command(DTO)

    def on_connection_error(self):
        QMessageBox.critical(self, "Error", "Připojení selhalo")

    def on_connection_success(self):
        # Dal jsem sem QTimer kvůli race condition. Z nějakého důvodu změna widgetu způsobí, že okno nereaguje na setFixedSize
        self.stacked.setCurrentWidget(self.panel_widget)
        QTimer.singleShot(20, lambda: self.setFixedSize(400,600))

    def on_connection_closed(self):
        # Dal jsem sem QTimer kvůli race condition. Z nějakého důvodu změna widgetu způsobí, že okno nereaguje na setFixedSize
        self.stacked.setCurrentWidget(self.connect_widget)
        QTimer.singleShot(20, lambda: self.setFixedSize(300, 50))
    def closeEvent(self, event):
        if self.tcp_client is None:
            return

        self.tcp_client.stop()
        event.accept()

    def on_data_received(self, DTO):
        if DTO.name != "get_status_response":
            return

        data = json.loads(DTO.args[0])

        # --- SHT3x ---
        sht_data = data["SHT3x"]

        sht_values = None
        if sht_data["values"] is not None:
            sht_values = TempData(
                temperature=sht_data["values"]["temperature"],
                humidity=sht_data["values"]["humidity"]
            )

        sht3x = SHT3x(
            connected=sht_data["connected"],
            values=sht_values
        )

        # --- MMA5452Q ---
        mma_data = data["MMA5452Q"]

        accel_values = None
        if mma_data["values_accel"] is not None:
            accel_values = AccelData(
                x=mma_data["values_accel"]["x"],
                y=mma_data["values_accel"]["y"],
                z=mma_data["values_accel"]["z"]
            )

        gyro_values = None
        if mma_data["values_gyro"] is not None:
            gyro_values = GyroData(
                roll=mma_data["values_gyro"]["roll"],
                pitch=mma_data["values_gyro"]["pitch"]
            )

        mma = MMA5452Q(
            connected=mma_data["connected"],
            values_accel=accel_values,
            values_gyro=gyro_values
        )

        result = GetStatusDTO(
            SHT3x=sht3x,
            MMA5452Q=mma
        )

        print(result)
