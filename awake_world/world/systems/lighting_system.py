from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LightingState:
    phase: str
    weather: str
    streetlights: bool
    interior_lights: bool
    global_exposure: float


class LightingSystem:
    """Produces cheap lighting intent; scenes implement it with washes, emissives and grouped lamps."""
    def resolve(self, phase: str, weather: str) -> LightingState:
        dark = phase in {"dawn", "dusk", "night"}
        exposure = {"dawn": .92, "day": 1.0, "dusk": .84, "night": .68}.get(phase, 1.0)
        if weather == "cloudy": exposure -= .07
        elif weather == "rain": exposure -= .13
        return LightingState(phase, weather, dark, dark or weather == "rain", max(.5, exposure))
