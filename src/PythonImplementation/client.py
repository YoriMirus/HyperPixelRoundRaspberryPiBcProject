import sys
import signal
import getpass
import socket
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPixmap, QPainter, QTransform, QFontDatabase
from PySide6.QtCore import Qt, QTimer, QCoreApplication

from widgets.ClientWindow import ClientWindow


def handle_sigint(sig, frame):
    print("Caught SIGINT, quitting...")
    QCoreApplication.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, handle_sigint)

    QFontDatabase.addApplicationFont("assets/SairaStencilOne-Regular.ttf")
    QFontDatabase.addApplicationFont("assets/Seven Segment.ttf")
    QFontDatabase.addApplicationFont("assets/digital-7 (mono).ttf")
    QFontDatabase.addApplicationFont("assets/digital-7.ttf")

    w = ClientWindow()
    w.show()
    sys.exit(app.exec())