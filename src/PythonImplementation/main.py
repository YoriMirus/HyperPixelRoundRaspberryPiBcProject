import sys
import signal
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

def handle_sigint(sig, frame):
    print("Caught SIGINT, quitting...")
    QApplication.quit()
    sys.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    is_raspberry_pi = is_pi_environment()
    signal.signal(signal.SIGINT, handle_sigint)

    if is_raspberry_pi:
        app.setOverrideCursor(Qt.BlankCursor)
        print("Raspberry Pi detected! Applying modifications...")

    QFontDatabase.addApplicationFont("assets/SairaStencilOne-Regular.ttf")
    QFontDatabase.addApplicationFont("assets/Seven Segment.ttf")

    w = MainWindow(is_raspberry_pi)
    w.pages[4].mapReady.connect(
        lambda: w.pages[4].setMapPosition(49.8322734, 18.1608531, 17)
    )
    w.show()
    sys.exit(app.exec())
