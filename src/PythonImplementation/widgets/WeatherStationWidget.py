from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QPainter, QTransform, QPen, QColor, QFontDatabase, QFont
from PySide6.QtCore import Qt, QTimer

class WeatherStationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480, 480)
        self.setStyleSheet("background-color: black;")

        QFontDatabase.addApplicationFont("assets/SairaStencilOne-Regular.ttf")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Invisible padding widget
        top_spacer = QWidget()
        top_spacer.setStyleSheet("background-color: transparent;")
        top_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(top_spacer, stretch=1)

        # ───────────────────────────────
        # Row 1 (flexible height)
        # ───────────────────────────────
        top_row_container = QWidget()
        top_row_container.setStyleSheet("background-color: transparent;")
        top_row_layout = QHBoxLayout(top_row_container)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(5)
        top_row_layout.setAlignment(Qt.AlignCenter)

        # humidity icon
        hum_icon = QLabel()
        hum_icon.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        hum_icon.setStyleSheet("background-color: transparent;")
        hum_pix = QPixmap("assets/humidity.png").scaled(
            64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        hum_icon.setPixmap(hum_pix)

        # humidity label
        hum_label = QLabel("69%")
        hum_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        hum_label.setStyleSheet("background-color: transparent;")
        hum_label.setStyleSheet("color: #4DA6FF;")
        hum_label.setFont(QFontDatabase.font("Saira Stencil One", "", 50))
        hum_label.setAlignment(Qt.AlignCenter)

        top_row_layout.addWidget(hum_icon)
        top_row_layout.addWidget(hum_label)

        layout.addWidget(top_row_container, stretch=0)

        # ───────────────────────────────
        # Row 2 (fixed 100 px)
        # ───────────────────────────────
        row2 = QLabel("11:28")
        row2.setAlignment(Qt.AlignCenter)
        row2.setFixedHeight(90)
        row2.setStyleSheet("color: white; background-color: transparent;")
        row2.setFont(QFontDatabase.font("Saira Stencil One", "", 100))
        #row2.setFont(QFont("Arial", 70))
        layout.addWidget(row2)

        # ───────────────────────────────
        # Row 3 (fixed 70 px)
        # ───────────────────────────────
        row3 = QLabel("PÁ 21.11.25")
        row3.setAlignment(Qt.AlignCenter)
        row3.setFixedHeight(80)
        row3.setStyleSheet("color: white; background-color: transparent;")
        row3.setFont(QFontDatabase.font("Saira Stencil One", "", 50))
        #row3.setFont(QFont("Arial", 50))
        layout.addWidget(row3)

        # ───────────────────────────────
        # Row 4 (flexible height)
        # ───────────────────────────────
        bottom_row_container = QWidget()
        bottom_row_container.setStyleSheet("background-color: transparent;")
        bottom_row_layout = QHBoxLayout(bottom_row_container)
        bottom_row_layout.setContentsMargins(0, 0, 0, 0)
        bottom_row_layout.setSpacing(10)
        bottom_row_layout.setAlignment(Qt.AlignCenter)

        # temperature icon
        temp_icon = QLabel()
        temp_pix = QPixmap("assets/temperature.png").scaled(
            64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        temp_icon.setPixmap(temp_pix)

        # humidity label
        temp_label = QLabel("21,0 °C")
        temp_label.setStyleSheet("color: #FF6B5A; background-color: transparent;")
        temp_label.setFont(QFontDatabase.font("Saira Stencil One", "", 40))
        temp_label.setAlignment(Qt.AlignCenter)

        bottom_row_layout.addWidget(temp_icon)
        bottom_row_layout.addWidget(temp_label)

        layout.addWidget(bottom_row_container, stretch=0)

        bottom_spacer = QWidget()
        bottom_spacer.setStyleSheet("background-color: transparent;")
        bottom_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(bottom_spacer, stretch=1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor("#00CC66"))
        pen.setWidth(10)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Circle centered in the widget
        painter.drawEllipse(5, 5, 470, 470)  # (480 - 10) because pen is 10px thick
