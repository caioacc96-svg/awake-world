from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsRectItem

from awake_world.design.material_light import resolve_space_appearance


PHASE_ORDER = ("dawn", "day", "dusk", "night")
PHASE_STARTS = {
    "dawn": 5 * 60 + 30,
    "day": 8 * 60,
    "dusk": 17 * 60 + 30,
    "night": 20 * 60,
}


def phase_for_minutes(minutes: float) -> str:
    m = int(minutes) % (24 * 60)
    if PHASE_STARTS["dawn"] <= m < PHASE_STARTS["day"]:
        return "dawn"
    if PHASE_STARTS["day"] <= m < PHASE_STARTS["dusk"]:
        return "day"
    if PHASE_STARTS["dusk"] <= m < PHASE_STARTS["night"]:
        return "dusk"
    return "night"


def format_world_time(minutes: float) -> str:
    m = int(minutes) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


@dataclass
class WorldClock:
    minutes: float = 8 * 60 + 24
    minutes_per_real_second: float = 0.5
    paused: bool = False

    @property
    def phase(self) -> str:
        return phase_for_minutes(self.minutes)

    def advance(self, dt: float) -> tuple[bool, bool]:
        old_minute = int(self.minutes)
        old_phase = self.phase
        if not self.paused:
            self.minutes = (self.minutes + dt * self.minutes_per_real_second) % (24 * 60)
        return int(self.minutes) != old_minute, self.phase != old_phase

    def jump_to_phase(self, phase: str) -> None:
        self.minutes = float(PHASE_STARTS[phase])

    def cycle_phase(self) -> str:
        current = self.phase
        index = PHASE_ORDER.index(current)
        target = PHASE_ORDER[(index + 1) % len(PHASE_ORDER)]
        self.jump_to_phase(target)
        return target


class SceneLightWash(QGraphicsRectItem):
    """Subtle global color wash. World objects still provide the actual local lighting."""

    COLORS = {
        "dawn": QColor(255, 205, 161, 24),
        "day": QColor(255, 255, 255, 0),
        "dusk": QColor(240, 139, 92, 30),
        "night": QColor(29, 37, 68, 78),
    }

    def __init__(self, rect: QRectF, phase: str, room_id: str | None = None) -> None:
        super().__init__(rect)
        self.room_id = room_id
        self.setPen(Qt.PenStyle.NoPen)
        self.setZValue(100000.0)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.set_phase(phase)

    def set_phase(self, phase: str) -> None:
        if self.room_id is not None:
            try:
                appearance = resolve_space_appearance(self.room_id, phase, "clear")
            except KeyError:
                appearance = None
            if appearance is not None:
                color = QColor(appearance.phase_wash)
                color.setAlpha(appearance.phase_wash_alpha)
                self.setBrush(color)
                return
        self.setBrush(self.COLORS.get(phase, self.COLORS["day"]))
