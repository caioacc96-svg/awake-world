from __future__ import annotations

from dataclasses import dataclass
import random

from awake_world.world.systems.subtle_life import SPACE_SUBTLE_LIFE_PROFILES


@dataclass(frozen=True, slots=True)
class AmbientEvent:
    key: str
    category: str
    space_id: str
    strength: float


EVENT_CATEGORIES = {
    "leaf_shift": "vegetation",
    "grass_wave": "vegetation",
    "garden_watering": "vegetation",
    "irrigation_cycle": "vegetation",
    "water_ripple": "atmosphere",
    "glass_rain": "atmosphere",
    "window_light": "atmosphere",
    "horizon_refresh": "atmosphere",
    "monitor_refresh": "technology",
    "server_blink": "technology",
    "status_cycle": "technology",
    "system_check": "technology",
    "build_refresh": "technology",
    "hardware_cycle": "technology",
    "instrument_cycle": "technology",
    "research_refresh": "technology",
    "charger_state": "technology",
    "match_state": "technology",
    "screen_refresh": "technology",
    "device_charge": "technology",
    "vent_cycle": "technology",
    "cafe_refresh": "social",
    "social_pause": "social",
    "collab_pause": "social",
    "courier_arrival": "service",
    "maintenance_pass": "service",
    "service_pass": "service",
    "tool_cycle": "service",
    "pet_pause": "animals",
    "bird_crossing": "animals",
    "distant_pass": "social",
    "blind_adjust": "architecture",
}

DEFAULT_EVENTS = ("window_light", "distant_pass", "monitor_refresh")


class AmbientLifeSystem:
    """Seeded, bounded ambient life driven by authored per-space profiles."""

    def __init__(self, seed: int = 404) -> None:
        self.seed = int(seed)
        self._rng = random.Random(self.seed)
        self._until_next = self._rng.uniform(3.2, 7.0)
        self.sequence = 0
        self.last_event: AmbientEvent | None = None

    def _profile_values(self, space_id: str) -> tuple[tuple[str, ...], float, float]:
        profile = SPACE_SUBTLE_LIFE_PROFILES.get(space_id)
        if profile is None:
            return DEFAULT_EVENTS, 3.2, 8.5
        return profile.event_keys, profile.cadence_min_s, profile.cadence_max_s

    def tick(self, dt: float, space_id: str, weather: str, minute: int) -> list[AmbientEvent]:
        events, cadence_min, cadence_max = self._profile_values(space_id)
        self._until_next -= max(0.0, float(dt))
        if self._until_next > 0.0:
            return []

        key = self._rng.choice(events)
        category = EVENT_CATEGORIES.get(key, "atmosphere")
        strength = self._rng.uniform(.22, .68)
        if weather == "rain" and category in {"vegetation", "atmosphere", "service"}:
            strength = min(.82, strength + .10)
        if minute % 1440 < 300 and category == "social":
            strength *= .45
        event = AmbientEvent(key, category, space_id, round(max(.08, min(.82, strength)), 3))
        self.last_event = event
        self.sequence += 1
        self._until_next = self._rng.uniform(cadence_min, cadence_max)
        return [event]

    def snapshot(self) -> dict[str, object]:
        event = self.last_event
        return {
            "sequence": self.sequence,
            "until_next": round(self._until_next, 3),
            "last": None if event is None else {
                "key": event.key,
                "category": event.category,
                "space_id": event.space_id,
                "strength": event.strength,
            },
        }
