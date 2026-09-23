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
        "courier_arrival": 24.0,
        "maintenance_pass": 26.0,
        "cafe_cycle": 22.0,
        "garden_watering": 30.0,
        "instrument_cycle": 18.0,
        "system_check": 16.0,
        "build_cycle": 20.0,
        "research_cycle": 24.0,
        "service_cycle": 22.0,
        "pet_pause": 18.0,
        "social_gathering": 34.0,
        "climate_cycle": 20.0,
        "dog_in_plaza": 34.0,
        "rooftop_session": 52.0,
        "power_flicker": 8.0,
        "server_issue": 24.0,
        "street_musician": 45.0,
    }

    SPACE_EVENTS = {
        "quarter": ("courier_arrival", "maintenance_pass"),
        "central_plaza": ("cafe_cycle", "garden_watering", "social_gathering"),
        "observatory": ("instrument_cycle",),
        "grid": ("system_check",),
        "twin_core": ("build_cycle", "server_issue"),
        "trinity_lab": ("research_cycle",),
        "garage": ("service_cycle",),
        "kawaii_garden": ("garden_watering", "pet_pause"),
        "pit": ("social_gathering",),
        "glasshouse": ("climate_cycle", "garden_watering"),
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
            event.remaining -= max(0.0, dt)
            if event.remaining <= 0:
                ended.append(key)
        for key in ended:
            event = self.active.pop(key)
            self.bus.publish(WorldEvent.MICROEVENT_ENDED, key=key, space_id=event.space_id)

        self._until_next -= max(0.0, dt)
        if self._until_next <= 0 and len(self.active) < 2:
            choices = self.SPACE_EVENTS.get(current_space, ("delivery",))
            key = self._rng.choice(choices)
            self.trigger(key, current_space)
            self._until_next = self._rng.uniform(78.0, 155.0)

    def snapshot(self) -> dict[str, float]:
        return {key: round(event.remaining, 2) for key, event in self.active.items()}
