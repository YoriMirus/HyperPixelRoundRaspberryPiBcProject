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

        conn = None
        client_ip = "unknown"

        while self._running:
            try:
                conn, addr = server.accept()
                self._socket = conn
                client_ip = addr[0]
                break
            except socket.timeout:
                continue

        if not conn:
            server.close()
            return

        conn.settimeout(self.timeout)

        self._receive_loop(client_ip)

        server.close()
