import sys
import getpass
import socket
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPixmap, QPainter, QTransform
from PySide6.QtCore import Qt, QTimer

from widgets.MainWindow import MainWindow

def is_pi_environment():
    user = getpass.getuser().lower()
    host = socket.gethostname().lower()
    return user in ("rpi", "raspberrypi") or host in ("rpi", "raspberrypi")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow(is_pi_environment())
    w.show()
    sys.exit(app.exec())
