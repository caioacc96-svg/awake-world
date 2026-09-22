from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AudioZone:
    id: str
    profile: str
    indoor: bool = False
    rain_surface: str = "open"
    gain: float = 1.0


class AudioZoneSystem:
    """Logical layered mixer; Qt Multimedia remains the playback backend."""
    RAIN_SURFACE_GAIN = {"open": 1.0, "glass": 0.72, "metal": 1.12, "vegetation": 0.82, "concrete": 0.92, "roof": 0.78}

    def __init__(self) -> None:
        self.current = AudioZone("world", "city_calm")
        self.previous = self.current
        self.transition = 1.0

    def enter(self, zone: AudioZone) -> None:
        self.previous = self.current
        self.current = zone
        self.transition = 0.0

    def tick(self, dt: float) -> None:
        self.transition = min(1.0, self.transition + max(0.0, dt) / 0.65)

    def mix(self, weather: str) -> dict[str, float]:
        surface = self.RAIN_SURFACE_GAIN.get(self.current.rain_surface, 1.0)
        rain = 0.0 if weather != "rain" else (0.40 if self.current.indoor else 0.82) * surface
        room = 0.58 if self.current.indoor else 0.14
        city = 0.24 if self.current.indoor else 0.62
        vegetation = 0.28 if self.current.profile in {"garden", "quiet_green", "plaza"} else 0.08
        technology = 0.34 if self.current.profile in {"servers", "quiet_tech", "observatory"} else 0.10
        return {
            "ambient": round(self.current.gain, 3), "city_hum": round(city, 3), "room_tone": round(room, 3),
            "rain": round(rain, 3), "vegetation": round(vegetation, 3), "technology": round(technology, 3),
            "zone_crossfade": round(self.transition, 3),
        }
