from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QPolygon, QFont
from PySide6.QtCore import Qt, QRect, QPoint, QPointF, QRectF
import math


class ColorCodingExample(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(480, 480)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # 1. Background & Outer Ring
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, 480, 480)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.drawEllipse(4, 4, 472, 472)

        # Move origin to center
        painter.translate(240, 240)

        # 2. Arcs
        arc_rect = QRect(-220, -220, 440, 440)
        start_angle = 225 * 16
        step_angle = 270 / 9
        step_qt = step_angle * 16

        painter.setPen(QPen(QColor(255, 255, 255), 8))
        painter.drawArc(arc_rect, start_angle - (step_qt * 2), -step_qt * 5)

        painter.setPen(QPen(QColor(0, 0, 255), 8))
        painter.drawArc(arc_rect, start_angle, -step_qt * 2)

        painter.setPen(QPen(QColor(255, 0, 0), 8))
        painter.drawArc(arc_rect, start_angle - (step_qt * 7), -step_qt * 2)

        # 3. Ticks and Labels (0, 10, 20...)
        painter.setFont(QFont("Arial", 24, QFont.Bold))

        for i in range(10):
            # Calculate angle for this tick (start at 135 degrees for bottom-left)
            angle_deg = 135 + (i * step_angle)
            angle_rad = math.radians(angle_deg)

            # Determine color
            color = QColor(255, 255, 255)
            if i <= 2:
                color = QColor(0, 0, 255)
            elif i >= 7:
                color = QColor(255, 0, 0)
            painter.setPen(QPen(color, 4))

            # Draw Ticks using rotation
            painter.save()
            painter.rotate(angle_deg)
            painter.drawLine(220, 0, 190, 0)
            painter.restore()

            # Draw Numbers (Positioned slightly inside the ticks)
            # We use math to keep the text upright
            val = str(i * 10)
            tx = 165 * math.cos(angle_rad)
            ty = 165 * math.sin(angle_rad)

            painter.setPen(QColor(255, 255, 255))
            # Draw text centered on the calculated point
            painter.drawText(QRectF(tx - 20, ty - 10, 40, 20), Qt.AlignCenter, val)

        # 4. Center Unit Label ("°C")
        painter.setFont(QFont("Arial", 36, QFont.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-50, 100, 100, 50), Qt.AlignCenter, "°C")

        # 5. Needle
        painter.save()
        painter.rotate(-90)  # Points needle to "50" by default
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawPolygon(QPolygon([QPoint(-50, -10), QPoint(200, 0), QPoint(-50, 10)]))
        painter.restore()

        # 6. Center Cap
        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(-30, -30, 60, 60)