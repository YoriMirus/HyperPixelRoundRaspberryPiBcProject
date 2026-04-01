import socket
from networking.TcpBase import BaseTcpThread


class TcpListener(BaseTcpThread):
    def __init__(self, host="0.0.0.0", port=5000, timeout=0.2):
        super().__init__(timeout)
        self.host = host
        self.port = port

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(1)
        server.settimeout(self.timeout)

        while self._running:
            try:
                conn, addr = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            self._socket = conn
            client_ip = addr[0]

            conn.settimeout(self.timeout)

            # Handle this client
            self._receive_loop(client_ip)

            # Clean up connection
            try:
                conn.close()
            except OSError:
                pass

            self._socket = None

        server.close()

