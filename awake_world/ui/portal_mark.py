from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QWidget


class PortalMark(QWidget):
    def __init__(self, color: str = "#5968F2", parent=None) -> None:
        super().__init__(parent)
        self.color = QColor(color)
        self.setFixedSize(28, 28)

    def sizeHint(self) -> QSize:
        return QSize(28, 28)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self.color)

        outer = QPainterPath()
        outer.addRoundedRect(QRectF(3, 3, 22, 22), 7, 7)
        p.drawPath(outer)

        p.setBrush(QColor("#FFFFFF"))
        inner = QPainterPath()
        inner.addRoundedRect(QRectF(9, 7, 10, 15), 4, 4)
        p.drawPath(inner)

        p.setBrush(self.color.darker(120))
        p.drawRoundedRect(QRectF(12.5, 10, 3, 10), 1.4, 1.4)
