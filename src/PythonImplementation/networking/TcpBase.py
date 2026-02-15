import json
import socket
from PySide6.QtCore import QThread, Signal, Slot
from networking.CommandDTO import CommandDTO


class BaseTcpThread(QThread):
    command_received = Signal(object)
    error = Signal(str)
    disconnected = Signal()

    def __init__(self, timeout=0.2):
        super().__init__()
        self.timeout = timeout
        self._running = True
        self._socket = None

    def _receive_loop(self, peer_ip: str):
        buffer = ""

        while self._running:
            try:
                data = self._socket.recv(1024)
                if not data:
                    break

                buffer += data.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self._handle_message(line, peer_ip)

            except socket.timeout:
                continue
            except OSError:
                break

        self._cleanup()

    def _handle_message(self, raw_message: str, peer_ip: str):
        try:
            parsed = json.loads(raw_message)

            command = CommandDTO(
                name=str(parsed["name"]),
                args=tuple(parsed["args"]),
                ip=peer_ip
            )

            self.command_received.emit(command)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print("Invalid message:", e)

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
        self.wait()

    def _cleanup(self):
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
            self.disconnected.emit()
