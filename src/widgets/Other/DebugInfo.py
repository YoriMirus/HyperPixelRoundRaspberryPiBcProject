from PySide6.QtWidgets import QApplication, QWidget, QFrame, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QTransform, QFontDatabase
from PySide6.QtCore import Qt, QTimer

from helpers.GetDebugInfo import get_hostname, get_all_ip_addresses

class DebugInfo(QWidget):
    def __init__(self, parent=None):
        super(DebugInfo, self).__init__(parent)

        # Povol úpravu pozadí + nastav ho na černé
        # Ve výchozím je totiž průhledné a jenom labely mají něco za sebou
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        self.main_layout = main_layout
        self.setLayout(main_layout)

        self.displayInfo()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onTimerUpdate)
        self.timer.start(1000)

    def displayInfo(self):
        self._clear_layout()

        spacerLabel = QLabel("")
        spacerLabel.setMinimumSize(50, 50)
        self.main_layout.addWidget(spacerLabel)

        hostnameLabel = QLabel(get_hostname())
        hostnameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hostnameLabel.setStyleSheet("font-size:40px; color: white")
        self.main_layout.addWidget(hostnameLabel)

        ip_addresses = get_all_ip_addresses()
        for ip_address in ip_addresses:
            ip_label = QLabel(ip_address)
            ip_label.setStyleSheet("font-size:40px; color: white")
            ip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(ip_label)

        spacerLabel = QLabel("")
        spacerLabel.setMinimumSize(50, 50)
        self.main_layout.addWidget(spacerLabel)

    def onTimerUpdate(self):
        self.displayInfo()

    def _clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout(child_layout)
