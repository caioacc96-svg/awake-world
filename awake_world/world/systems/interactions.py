from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Iterable, Protocol


class InteractionLike(Protocol):
    x: float
    y: float
    radius: float


@dataclass(slots=True)
class InteractionContext:
    space_id: str
    actor_id: str = "local_player"
    access: str = "awake_members"


class InteractionSystem:
    """Contextual target scoring with hysteresis, facing, height and forgiving retention."""

    def __init__(self, switch_margin: float = 0.12, linger_multiplier: float = 1.16) -> None:
        self.switch_margin = float(switch_margin)
        self.linger_multiplier = float(linger_multiplier)
        self._current: InteractionLike | None = None

    @staticmethod
    def _score(
        item: InteractionLike,
        x: float,
        y: float,
        facing: tuple[float, float] | None,
        actor_z: float = 0.0,
    ) -> float:
        dx = float(item.x) - x
        dy = float(item.y) - y
        distance = hypot(dx, dy)
        radius = max(0.001, float(item.radius))
        target_z = float(getattr(item, "z", 0.0))
        elevation_delta = abs(target_z - actor_z)
        if distance > radius or elevation_delta > .62:
            return float("-inf")
        distance_score = 1.0 - distance / radius
        height_score = max(0.0, 1.0 - elevation_delta / .62) * .10
        facing_score = 0.0
        if facing and distance > 1e-6:
            fx, fy = facing
            flen = hypot(fx, fy)
            if flen > 1e-6:
                facing_score = max(-1.0, min(1.0, (fx * dx + fy * dy) / (flen * distance))) * 0.22
        priority = float(getattr(item, "priority", 0.0)) * 0.08
        return distance_score + height_score + facing_score + priority

    def nearest(
        self,
        interactions: Iterable[InteractionLike],
        x: float,
        y: float,
        facing: tuple[float, float] | None = None,
        actor_z: float = 0.0,
    ):
        items = list(interactions)
        best = None
        best_score = float("-inf")
        for item in items:
            score = self._score(item, x, y, facing, actor_z)
            if score > best_score:
                best, best_score = item, score

        current = self._current
        if current is not None and current in items:
            dist = hypot(current.x - x, current.y - y)
            current_score = self._score(current, x, y, facing, actor_z)
            if dist <= current.radius * self.linger_multiplier and current_score != float("-inf"):
                if best is None or best is current or best_score < current_score + self.switch_margin:
                    return current
        self._current = best
        return best

    @property
    def current(self):
        return self._current

    def clear(self) -> None:
        self._current = None
