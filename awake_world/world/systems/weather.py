from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import random

from awake_world.world.systems.events import EventBus, WorldEvent


class WeatherKind(StrEnum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"


@dataclass(slots=True)
class WeatherSnapshot:
    kind: WeatherKind = WeatherKind.CLEAR
    intensity: float = 0.0
    transition: float = 1.0


class WeatherSystem:
    """Cheap systemic weather: deterministic state machine, expensive effects stay presentation-side."""

    def __init__(self, bus: EventBus, kind: str = "clear", intensity: float = 0.0, seed: int = 404) -> None:
        self.bus = bus
        self.state = WeatherSnapshot(WeatherKind(kind), float(intensity), 1.0)
        self._age = 0.0
        self._next_auto_change = 150.0
        self._rng = random.Random(int(seed))

    def set(self, kind: WeatherKind | str, intensity: float | None = None) -> None:
        new_kind = WeatherKind(kind)
        old = self.state.kind
        if intensity is None:
            intensity = {WeatherKind.CLEAR: 0.0, WeatherKind.CLOUDY: 0.35, WeatherKind.RAIN: 0.72}[new_kind]
        self.state = WeatherSnapshot(new_kind, max(0.0, min(float(intensity), 1.0)), 0.0)
        self._age = 0.0
        self._next_auto_change = self._rng.uniform(120.0, 240.0)
        if old != new_kind:
            self.bus.publish(WorldEvent.WEATHER_CHANGED, old=old.value, weather=new_kind.value, intensity=self.state.intensity)

    def tick(self, dt: float, auto: bool = True) -> None:
        self._age += dt
        self.state.transition = min(1.0, self.state.transition + dt * 0.35)
        if auto and self._age >= self._next_auto_change:
            choices = {
                WeatherKind.CLEAR: (WeatherKind.CLEAR, WeatherKind.CLOUDY),
                WeatherKind.CLOUDY: (WeatherKind.CLEAR, WeatherKind.CLOUDY, WeatherKind.RAIN),
                WeatherKind.RAIN: (WeatherKind.CLOUDY, WeatherKind.CLEAR),
            }[self.state.kind]
            self.set(self._rng.choice(choices))
