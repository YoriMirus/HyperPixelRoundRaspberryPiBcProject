from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QWidget, QStackedLayout
from PySide6.QtGui import QPixmap, QPainter, QColor, Qt


class LevelWidget(QLabel):
    def __init__(self, parent=None):
        super(LevelWidget, self).__init__(parent)
        self.setFixedSize(480,480)

        # 120 Hz. Displej má 60 fps tak dejme dvojnásobek, aby náhodou nebyly přeskočené snímky
        self.timer_refresh_rate = 120

        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.on_timer_tick)
        self.main_timer.start(int((1.0/self.timer_refresh_rate)*1000))

        self.bubble = QLabel()
        self.bubble.setPixmap(QPixmap("assets/bubble.png"))
        self.bubble.setScaledContents(True)
        self.bubble.setAttribute(Qt.WA_TranslucentBackground)
        self.bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bubble.setFixedSize(60, 60)
        self.bubble.move(0, 0)

        main_layout = QStackedLayout(self)
        main_layout.setStackingMode(QStackedLayout.StackAll)

        # Overlay (managed by layout)
        self.overlay_widget = QLabel()
        self.overlay_widget.setStyleSheet("""
        background-color: rgba(120, 255, 80, 120);
""")
        self.overlay_widget.raise_()
        main_layout.addWidget(self.bubble)
        main_layout.addWidget(self.overlay_widget)

    def on_timer_tick(self):
        self.update()