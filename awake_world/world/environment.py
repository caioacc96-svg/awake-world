from __future__ import annotations

import math
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem

from awake_world.design.material_light import resolve_space_appearance


class WeatherWash(QGraphicsRectItem):
    COLORS = {
        "clear": QColor(255, 255, 255, 0),
        "cloudy": QColor(95, 110, 128, 32),
        "rain": QColor(53, 69, 92, 58),
    }

    def __init__(
        self,
        rect: QRectF,
        weather: str = "clear",
        room_id: str | None = None,
        phase: str = "day",
    ) -> None:
        super().__init__(rect)
        self.room_id = room_id
        self.phase = phase
        self.setPen(Qt.PenStyle.NoPen)
        self.setZValue(99990)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.set_weather(weather)

    def set_weather(self, weather: str) -> None:
        if self.room_id is not None:
            try:
                appearance = resolve_space_appearance(self.room_id, self.phase, weather)
            except KeyError:
                appearance = None
            if appearance is not None:
                color = QColor(appearance.weather_wash)
                color.setAlpha(appearance.weather_wash_alpha)
                self.setBrush(color)
                return
        self.setBrush(self.COLORS.get(weather, self.COLORS["clear"]))


class RainStreak(QGraphicsLineItem):
    def __init__(self, rect: QRectF, index: int) -> None:
        super().__init__()
        self.rect = rect
        self.index = index
        self.phase = (index * 0.137) % 1.0
        self.speed = 0.28 + (index % 7) * 0.018
        self.x_ratio = ((index * 37) % 101) / 100.0
        self.setPen(QPen(QColor(190, 214, 235, 92), 1.0 + (index % 3) * 0.2))
        self.setZValue(99995 + (index % 4))
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._sync()

    def _sync(self) -> None:
        y = self.rect.top() + self.phase * self.rect.height()
        x = self.rect.left() + self.x_ratio * self.rect.width()
        length = 10 + (self.index % 6) * 2
        self.setLine(x, y, x - 4, y + length)

    def advance_animation(self, dt: float) -> None:
        self.phase = (self.phase + dt * self.speed) % 1.0
        drift = math.sin(self.phase * math.tau + self.index) * 0.004
        self.x_ratio = (self.x_ratio + drift * dt) % 1.0
        self._sync()
