import sys
import getpass
import socket
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPixmap, QPainter, QTransform, QFontDatabase
from PySide6.QtCore import Qt, QTimer

from widgets.MainWindow import MainWindow

def is_pi_environment():
    user = getpass.getuser().lower()
    host = socket.gethostname().lower()
    return user in ("rpi", "raspberrypi") or host in ("rpi", "raspberrypi")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    is_raspberry_pi = is_pi_environment()

    if is_raspberry_pi:
        app.setOverrideCursor(Qt.BlankCursor)
        print("Raspberry Pi detected! Applying modifications...")

    QFontDatabase.addApplicationFont("assets/SairaStencilOne-Regular.ttf")

    w = MainWindow(is_raspberry_pi)
    w.pages[4].mapReady.connect(
        lambda: w.pages[4].setMapPosition(49.8322734, 18.1608531, 17)
    )
    w.show()
    sys.exit(app.exec())
