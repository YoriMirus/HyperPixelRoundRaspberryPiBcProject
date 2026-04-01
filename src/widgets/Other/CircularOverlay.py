from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QRegion, QColor, QPainter
from PySide6.QtCore import QRect, Qt

class CircularOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(0, 0, 480, 480)

        # důležité: nechceme blokovat vstupy
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.update_mask()

    def update_mask(self):
        rect = self.rect()
        region = QRegion(rect)

        # střed + radius (uprav dle potřeby)
        cx, cy = 240, 240
        r = 240

        circle = QRegion(
            QRect(cx - r, cy - r, 2*r, 2*r),
            QRegion.Ellipse
        )

        region = region.subtracted(circle)
        self.setMask(region)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor("white"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())