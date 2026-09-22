from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from awake_world.world.state import WorldState
    from awake_world.world.systems.events import EventBus, WorldEvent
    from awake_world.world.systems.microevents import MicroEventSystem
    from awake_world.world.systems.performance import PerformanceSystem
    from awake_world.world.systems.runtime import WorldRuntime
    from awake_world.world.systems.spaces import (
        SPACE_CATALOG,
        PersonalSpace,
        SharedStudio,
        SocialSpace,
        SpaceSystem,
    )
    from awake_world.world.systems.weather import WeatherKind, WeatherSystem

    events: list[tuple[WorldEvent, dict]] = []
    bus = EventBus()
    bus.subscribe(WorldEvent.WEATHER_CHANGED, lambda event: events.append((event.kind, event.payload)))
    weather = WeatherSystem(bus)
    weather.set(WeatherKind.RAIN)
    assert weather.state.kind is WeatherKind.RAIN
    assert events and events[-1][0] is WorldEvent.WEATHER_CHANGED

    micro = MicroEventSystem(bus, {"delivery": 5.0})
    assert "delivery" in micro.active
    micro.tick(6.0, "quarter")
    assert "delivery" not in micro.active

    state = WorldState()
    runtime = WorldRuntime(state, minutes_per_real_second=1.0)
    assert runtime.current_space == "quarter"
    assert runtime.time.phase == "day"
    runtime.enter_space("observatory")
    assert runtime.current_space == "observatory"
    assert state.last_room == "observatory"
    assert state.presence["local_player"]["space_id"] == "observatory"
    runtime.set_weather("cloudy")
    assert state.weather == "cloudy"
    runtime.microevents.trigger("server_issue", "twin_core", 10.0)
    runtime.tick(1.0)
    assert 8.9 <= state.active_events["server_issue"] <= 9.1
    assert state.npc_states
    assert runtime.audio_mix()["ambient"] > 0
    assert runtime.resolved_lighting().phase == runtime.time.phase

    # TimeSystem preserves the old WorldClock-facing API while publishing state.
    before = state.world_minutes
    runtime.time.advance(2.0)
    assert state.world_minutes > before
    runtime.time.minutes = 18 * 60
    assert runtime.time.phase == "dusk"

    spaces = SpaceSystem(state)
    assert isinstance(SPACE_CATALOG["quarter"], SocialSpace)
    assert isinstance(SPACE_CATALOG["observatory"], PersonalSpace)
    assert isinstance(SPACE_CATALOG["twin_core"], SharedStudio)
    assert spaces.exists("kawaii_garden")

    perf = PerformanceSystem()
    assert perf.simulation_lod(5) == "full"
    assert perf.simulation_lod(20) == "reduced"
    assert perf.simulation_lod(50) == "logical_only"

    # Persistence round trip, including Build 0.4.1 living-city fields.
    import awake_world.world.save as save_module

    temp_root = Path(tempfile.mkdtemp(prefix="awake-core-save-"))
    save_module.SAVE_DIR = temp_root
    save_module.SAVE_FILE = temp_root / "single_player_save.json"
    save_module.BACKUP_FILE = temp_root / "single_player_save.backup.json"
    save_module.RECOVERY_FILE = temp_root / "single_player_save.recovery.json"
    save_module.CORRUPT_DIR = temp_root / "corrupt"
    save_module.save_state(state)
    loaded = save_module.load_state()
    assert loaded.last_room == state.last_room
    assert loaded.weather == state.weather
    assert loaded.active_events == state.active_events
    assert loaded.presence == state.presence
    assert loaded.npc_states == state.npc_states

    print("AWAKE_CORE_SYSTEMS_OK")
    print(f"spaces={len(SPACE_CATALOG)} events={len(events)} save_version={loaded.schema_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
