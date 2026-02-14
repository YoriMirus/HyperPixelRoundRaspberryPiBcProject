from PySide6.QtWidgets import QWidget, QMessageBox, QStackedLayout

from networking.TcpClient import TcpClient

from widgets.Client.ConnectionWidget import ConnectionWidget
from widgets.Client.ClientPanel import ClientPanel

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

        self.tcp_client.start()

    def on_command_send_request(self, DTO):
        self.tcp_client.send_command(DTO)

    def on_connection_error(self):
        QMessageBox.critical(self, "Error", "Připojení selhalo")

    def on_connection_success(self):
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
