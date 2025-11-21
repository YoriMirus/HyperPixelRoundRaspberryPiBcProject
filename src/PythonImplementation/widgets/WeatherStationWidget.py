from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtGui import QPixmap, QPainter, QTransform
from PySide6.QtCore import Qt, QTimer

class WeatherStationWidget(QWidget):
    def __init__(self, parent=None):
        super(WeatherStationWidget, self).__init__(parent)
        self.main_label = QLabel(self)
        self.main_label.setText("Zkušební text")
        self.main_label.setGeometry(0, 220, 480, 40)
