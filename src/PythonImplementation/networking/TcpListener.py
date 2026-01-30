import socket
import json
from PySide6.QtCore import QThread, Signal

from networking.CommandDTO import CommandDTO

class TcpListener(QThread):
    command_received = Signal(object)

    def __init__(self, host="0.0.0.0", port=5000, timeout=0.2):
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self._running = True

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(1)
        server.settimeout(self.timeout)

        conn = None

        client_ip = "unknown"

        # ---- Wait for a client (interruptible) ----
        while self._running:
            try:
                conn, addr = server.accept()
                client_ip = addr[0]
                break
            except socket.timeout:
                continue

        if not conn:
            server.close()
            return

        conn.settimeout(self.timeout)
        buffer = ""

        # ---- Receive loop ----
        while self._running:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                buffer += data.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self._handle_message(line, client_ip)

            except socket.timeout:
                continue
            except OSError:
                break

        conn.close()
        server.close()

    def _handle_message(self, raw_message: str, client_ip: str):
        try:
            parsed = json.loads(raw_message)

            command = CommandDTO(
                name=str(parsed["name"]),
                args=tuple(parsed["args"]),
                ip=client_ip
            )

            self.command_received.emit(command)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print("Invalid message:", e)

    def stop(self):
        self._running = False
        self.wait()