from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True, slots=True)
class AmbientEvent:
    key: str
    category: str
    space_id: str
    strength: float


class AmbientLifeSystem:
    """Low-frequency seeded ambient life; presentation decides how each event is rendered."""

    CATALOG = (
        ("leaf_shift", "vegetation"), ("grass_wave", "vegetation"),
        ("monitor_refresh", "technology"), ("server_blink", "technology"),
        ("door_use", "architecture"), ("blind_adjust", "architecture"),
        ("coffee_steam", "social"), ("distant_pass", "social"),
        ("bird_crossing", "animals"), ("window_light", "atmosphere"),
        ("water_ripple", "atmosphere"), ("sign_pulse", "technology"),
    )

    def __init__(self, seed: int = 404) -> None:
        self.seed = int(seed)
        self._rng = random.Random(self.seed)
        self._until_next = self._rng.uniform(2.5, 6.0)
        self.sequence = 0

    def tick(self, dt: float, space_id: str, weather: str, minute: int) -> list[AmbientEvent]:
        self._until_next -= max(0.0, dt)
        if self._until_next > 0.0:
            return []
        key, category = self._rng.choice(self.CATALOG)
        strength = self._rng.uniform(0.25, 0.78)
        if weather == "rain" and category in {"vegetation", "atmosphere"}:
            strength = min(1.0, strength + 0.15)
        if minute % 1440 < 300 and category == "social":
            strength *= 0.45
        self.sequence += 1
        self._until_next = self._rng.uniform(3.2, 9.0)
        return [AmbientEvent(key, category, space_id, round(strength, 3))]
