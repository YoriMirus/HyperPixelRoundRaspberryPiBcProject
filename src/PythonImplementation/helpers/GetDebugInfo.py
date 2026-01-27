import socket
import psutil


def get_hostname() -> str:
    return socket.gethostname()


def get_all_ip_addresses() -> list[str]:
    ip_addresses = []

    for addrs in psutil.net_if_addrs().values():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                if not addr.address.startswith("127."):
                    ip_addresses.append(addr.address)

    return ip_addresses
