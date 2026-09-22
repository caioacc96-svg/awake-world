from __future__ import annotations

from dataclasses import dataclass
import random

from awake_world.world.systems.events import EventBus, WorldEvent


@dataclass(slots=True)
class ActiveMicroEvent:
    key: str
    remaining: float
    space_id: str | None = None


class MicroEventSystem:
    CATALOG = {
        "delivery": 28.0,
        "dog_in_plaza": 34.0,
        "rooftop_session": 52.0,
        "power_flicker": 8.0,
        "server_issue": 24.0,
        "street_musician": 45.0,
    }

    def __init__(self, bus: EventBus, initial: dict[str, float] | None = None, seed: int = 704) -> None:
        self.bus = bus
        self.active: dict[str, ActiveMicroEvent] = {}
        self._rng = random.Random(int(seed) + 300)
        self._until_next = 70.0
        self.restore(initial or {})

    def restore(self, data: dict[str, float]) -> None:
        self.active.clear()
        for key, remaining in data.items():
            if key not in self.CATALOG:
                continue
            value = max(0.0, float(remaining))
            if value > 0:
                self.active[key] = ActiveMicroEvent(key, value, None)

    def trigger(self, key: str, space_id: str | None = None, duration: float | None = None) -> None:
        if key not in self.CATALOG and duration is None:
            duration = 20.0
        duration = float(duration or self.CATALOG.get(key, 20.0))
        self.active[key] = ActiveMicroEvent(key, duration, space_id)
        self.bus.publish(WorldEvent.MICROEVENT_STARTED, key=key, space_id=space_id, duration=duration)

    def tick(self, dt: float, current_space: str) -> None:
        ended: list[str] = []
        for key, event in tuple(self.active.items()):
            event.remaining -= dt
            if event.remaining <= 0:
                ended.append(key)
        for key in ended:
            event = self.active.pop(key)
            self.bus.publish(WorldEvent.MICROEVENT_ENDED, key=key, space_id=event.space_id)

        self._until_next -= dt
        if self._until_next <= 0 and len(self.active) < 2:
            key = self._rng.choice(tuple(self.CATALOG))
            self.trigger(key, current_space if key in {"power_flicker", "server_issue"} else None)
            self._until_next = self._rng.uniform(75.0, 150.0)

    def snapshot(self) -> dict[str, float]:
        return {key: round(event.remaining, 2) for key, event in self.active.items()}
