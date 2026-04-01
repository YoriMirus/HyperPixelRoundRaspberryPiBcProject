import socket
from PySide6.QtCore import Signal

from networking.TcpBase import BaseTcpThread


class TcpClient(BaseTcpThread):
    connected = Signal()

    def __init__(self, host: str, port: int, timeout=0.2):
        super().__init__(timeout)
        self.host = host
        self.port = port

    def run(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))
            self.connected.emit()
        except OSError as e:
            self.error.emit(str(e))
            self._cleanup()
            return

        self._receive_loop(self.host)
