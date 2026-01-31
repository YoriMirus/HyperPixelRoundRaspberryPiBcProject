from PySide6.QtWidgets import QApplication, QWidget, QFrame, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QTransform, QFontDatabase
from PySide6.QtCore import Qt, QTimer

from helpers.GetDebugInfo import get_hostname, get_all_ip_addresses

class DebugInfo(QWidget):
    def __init__(self, parent=None):
        super(DebugInfo, self).__init__(parent)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout)

        spacerLabel = QLabel("")
        spacerLabel.setMinimumSize(50,50)
        main_layout.addWidget(spacerLabel)

        hostnameLabel = QLabel(get_hostname())
        hostnameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hostnameLabel.setStyleSheet("font-size:40px;")
        main_layout.addWidget(hostnameLabel)

        ip_addresses = get_all_ip_addresses()
        for ip_address in ip_addresses:
            ip_label = QLabel(ip_address)
            ip_label.setStyleSheet("font-size:40px;")
            ip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(ip_label)

        spacerLabel = QLabel("")
        spacerLabel.setStyleSheet("font-size:40px;")
        spacerLabel.setMinimumSize(50,50)
        main_layout.addWidget(spacerLabel)
