import sys
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPixmap, QPainter, QTransform
from PySide6.QtCore import Qt, QTimer

from widgets.ClockWidget import ClockWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ClockWidget()
    w.show()
    sys.exit(app.exec())
