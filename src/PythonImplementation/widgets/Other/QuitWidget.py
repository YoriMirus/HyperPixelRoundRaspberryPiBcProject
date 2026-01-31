import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QCoreApplication

class QuitWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480,480)

        # Create the round exit button
        btn = QPushButton("✕")
        btn.setFixedSize(160, 160)   # size of the round button (change if needed)
        btn.clicked.connect(QApplication.quit)


        # Style it
        btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                font-size: 64px;
                border: 2px solid white;
                border-radius: 80px;   /* half of width/height → circle */
            }
            QPushButton:pressed {
                background-color: #000000;
                color: white;
            }
        """)

        layout = QHBoxLayout(self)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.setWindowTitle("Exit Button")
