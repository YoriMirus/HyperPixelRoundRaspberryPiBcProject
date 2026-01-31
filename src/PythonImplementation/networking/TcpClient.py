import socket
import json

from PySide6.QtCore import QThread, Signal, Slot

from networking.CommandDTO import CommandDTO


class TcpClient(QThread):
    connected = Signal()
    disconnected = Signal()
    error = Signal(str)

    def __init__(self, host: str, port: int, timeout=0.2):
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self._running = True
        self._socket = None

    def run(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))
            self.connected.emit()
        except OSError as e:
            self.error.emit(str(e))
            return

        # Optional receive loop (can be removed if you don't expect replies)
        while self._running:
            try:
                data = self._socket.recv(1024)
                if not data:
                    break
            except socket.timeout:
                continue
            except OSError:
                break

        self._cleanup()

    @Slot(object)
    def send_command(self, command: CommandDTO):
        if not self._socket:
            return

        try:
            payload = {
                "name": command.name,
                "args": list(command.args)
            }

            message = json.dumps(payload) + "\n"
            self._socket.sendall(message.encode())

        except OSError as e:
            self.error.emit(str(e))

    def stop(self):
        self._running = False
        self._cleanup()
        self.wait()

    def _cleanup(self):
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
            self.disconnected.emit()
