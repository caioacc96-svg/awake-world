from __future__ import annotations

from dataclasses import dataclass, field

from awake_world.world.progression import STARTER_DECOR


@dataclass
class WorldState:
    schema_version: int = 6
    build_version: str = "0.5.0-dev"
    world_seed: int = 404
    discovered: set[str] = field(default_factory=set)
    toggles: dict[str, bool] = field(default_factory=dict)
    visits: dict[str, int] = field(default_factory=dict)
    world_minutes: float = 8 * 60 + 24
    inventory: set[str] = field(default_factory=lambda: set(STARTER_DECOR))
    decor: dict[str, str] = field(default_factory=dict)
    flags: set[str] = field(default_factory=set)
    conversations: dict[str, int] = field(default_factory=dict)
    journal: list[str] = field(default_factory=lambda: ["arrival"])
    last_room: str = "quarter"
    weather: str = "clear"
    weather_intensity: float = 0.0
    active_events: dict[str, float] = field(default_factory=dict)
    district_states: dict[str, dict[str, object]] = field(default_factory=dict)
    space_states: dict[str, dict[str, object]] = field(default_factory=dict)
    npc_states: dict[str, dict[str, object]] = field(default_factory=dict)
    pet_states: dict[str, dict[str, object]] = field(default_factory=dict)
    presence: dict[str, dict[str, object]] = field(default_factory=dict)
    environment_state: dict[str, object] = field(default_factory=dict)
    player_state: dict[str, object] = field(default_factory=dict)
