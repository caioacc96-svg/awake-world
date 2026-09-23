from __future__ import annotations

from dataclasses import dataclass
from math import sin


@dataclass(frozen=True, slots=True)
class LifeAnchor:
    kind: str
    x: float
    y: float
    scale: float = 1.0
    purpose: str = ""


@dataclass(frozen=True, slots=True)
class SubtleLifeProfile:
    space_id: str
    cadence_min_s: float
    cadence_max_s: float
    vegetation_amplitude_deg: float
    vegetation_speed: float
    event_keys: tuple[str, ...]
    occupancy_traces: tuple[LifeAnchor, ...]
    state_anchors: tuple[LifeAnchor, ...]
    room_tone: str
    weather_response: str

    def motion(self, seconds: float, phase: float = 0.0) -> float:
        amplitude = min(1.85, max(0.0, self.vegetation_amplitude_deg))
        speed = min(1.35, max(0.15, self.vegetation_speed))
        return sin(seconds * speed + phase) * amplitude


SPACE_SUBTLE_LIFE_PROFILES: dict[str, SubtleLifeProfile] = {
    "quarter": SubtleLifeProfile(
        "quarter", 3.8, 8.8, 1.10, .62,
        ("distant_pass", "courier_arrival", "maintenance_pass", "window_light", "bird_crossing"),
        (
            LifeAnchor("parcel", 15.6, 8.9, .75, "courier route handoff"),
            LifeAnchor("cup", 10.2, 9.8, .70, "brief plaza stop"),
        ),
        (LifeAnchor("wayfinding", 11.8, 7.8, .78, "district status"),),
        "city_calm", "wet stone + sheltered circulation",
    ),
    "central_plaza": SubtleLifeProfile(
        "central_plaza", 3.4, 8.0, 1.25, .68,
        ("cafe_refresh", "social_pause", "garden_watering", "distant_pass"),
        (
            LifeAnchor("cup", 3.7, 6.0, .82, "cafe service"),
            LifeAnchor("notebook", 8.6, 8.8, .78, "informal meeting"),
        ),
        (LifeAnchor("cafe_display", 4.1, 5.2, .82, "cafe state"),),
        "plaza", "canopy shelter + garden runoff",
    ),
    "observatory": SubtleLifeProfile(
        "observatory", 5.4, 11.0, .72, .44,
        ("instrument_cycle", "horizon_refresh", "blind_adjust"),
        (
            LifeAnchor("notebook", 7.4, 7.4, .76, "active project study"),
            LifeAnchor("cup", 9.1, 7.7, .66, "long-form work"),
        ),
        (LifeAnchor("instrument", 8.5, 2.9, .90, "observatory instrument"),),
        "observatory", "glass hush + distant rain",
    ),
    "grid": SubtleLifeProfile(
        "grid", 3.1, 7.2, .58, .52,
        ("system_check", "monitor_refresh", "status_cycle"),
        (
            LifeAnchor("tablet", 6.2, 6.1, .72, "operations queue"),
            LifeAnchor("notebook", 9.4, 7.8, .68, "handoff notes"),
        ),
        (LifeAnchor("ops_display", 7.5, 5.6, .86, "operations state"),),
        "quiet_tech", "sealed operational response",
    ),
    "twin_core": SubtleLifeProfile(
        "twin_core", 2.9, 6.8, .48, .58,
        ("build_refresh", "server_blink", "hardware_cycle", "system_check"),
        (
            LifeAnchor("device", 6.8, 7.9, .78, "hardware prototype"),
            LifeAnchor("cup", 10.5, 8.2, .62, "paired dev session"),
        ),
        (
            LifeAnchor("dev_display", 6.9, 4.7, .86, "build state"),
            LifeAnchor("dev_display", 10.2, 4.7, .86, "runtime state"),
        ),
        "servers", "metal/glass rain isolation",
    ),
    "trinity_lab": SubtleLifeProfile(
        "trinity_lab", 3.3, 7.6, .70, .55,
        ("instrument_cycle", "research_refresh", "collab_pause"),
        (
            LifeAnchor("paper", 7.1, 8.9, .72, "research notes"),
            LifeAnchor("device", 10.4, 9.0, .72, "active experiment"),
        ),
        (LifeAnchor("lab_display", 8.6, 2.8, .84, "research cycle"),),
        "quiet_tech", "terrace moisture + warm interior",
    ),
    "garage": SubtleLifeProfile(
        "garage", 3.0, 7.0, .35, .46,
        ("tool_cycle", "service_pass", "charger_state"),
        (
            LifeAnchor("tool", 6.1, 7.5, .78, "recent bench use"),
            LifeAnchor("package", 3.2, 9.0, .74, "parts delivery"),
        ),
        (LifeAnchor("bench_display", 8.0, 6.8, .78, "workbench diagnostic"),),
        "workshop", "metal roof + door runoff",
    ),
    "kawaii_garden": SubtleLifeProfile(
        "kawaii_garden", 3.2, 7.4, 1.65, .78,
        ("leaf_shift", "garden_watering", "pet_pause", "water_ripple"),
        (
            LifeAnchor("watering_can", 4.0, 9.7, .72, "garden care"),
            LifeAnchor("toy", 10.7, 8.8, .60, "pet occupancy"),
        ),
        (LifeAnchor("garden_sensor", 8.4, 5.4, .70, "irrigation state"),),
        "garden", "leaf + water response",
    ),
    "pit": SubtleLifeProfile(
        "pit", 2.8, 6.4, .24, .38,
        ("match_state", "social_pause", "screen_refresh", "device_charge"),
        (
            LifeAnchor("controller", 7.4, 6.0, .74, "recent play"),
            LifeAnchor("cup", 9.0, 6.2, .62, "social occupancy"),
        ),
        (
            LifeAnchor("pit_display", 6.4, 5.0, .76, "session state"),
            LifeAnchor("pit_display", 9.5, 5.0, .76, "session state"),
        ),
        "gaming_den", "subterranean muted rain",
    ),
    "glasshouse": SubtleLifeProfile(
        "glasshouse", 3.4, 7.8, 1.48, .72,
        ("vent_cycle", "irrigation_cycle", "leaf_shift", "glass_rain"),
        (
            LifeAnchor("shears", 3.3, 8.6, .68, "plant care"),
            LifeAnchor("notebook", 8.1, 5.2, .70, "growth notes"),
        ),
        (LifeAnchor("climate_display", 8.4, 4.8, .72, "climate state"),),
        "quiet_green", "glass runoff + ventilation",
    ),
}


def get_subtle_life_profile(space_id: str) -> SubtleLifeProfile:
    return SPACE_SUBTLE_LIFE_PROFILES[space_id]


def validate_subtle_life_contract() -> tuple[str, ...]:
    failures: list[str] = []
    for space_id, profile in SPACE_SUBTLE_LIFE_PROFILES.items():
        if profile.cadence_min_s < 2.5 or profile.cadence_max_s > 12.0:
            failures.append(f"{space_id}:cadence")
        if profile.cadence_min_s >= profile.cadence_max_s:
            failures.append(f"{space_id}:cadence_order")
        if not 0.0 <= profile.vegetation_amplitude_deg <= 1.85:
            failures.append(f"{space_id}:vegetation_amplitude")
        if not profile.event_keys or not profile.occupancy_traces or not profile.state_anchors:
            failures.append(f"{space_id}:authored_life_missing")
        if not profile.room_tone or not profile.weather_response:
            failures.append(f"{space_id}:atmosphere_missing")
    return tuple(failures)
