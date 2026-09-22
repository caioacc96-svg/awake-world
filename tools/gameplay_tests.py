from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from awake_world.presentation.transition_orchestrator import PROFILES, SpaceTransitionOrchestrator
from awake_world.simulation import ActorRuntime, Vec2
from awake_world.world.state import WorldState
from awake_world.world.systems.interactions import InteractionSystem
from awake_world.world.systems.runtime import WorldRuntime


@dataclass(frozen=True)
class Target:
    x: float
    y: float
    radius: float
    key: str


def run() -> dict[str, str]:
    results: dict[str, str] = {}

    # TEST_PLAYER_WALK_QUARTER
    state = WorldState(world_seed=404)
    runtime = WorldRuntime(state, minutes_per_real_second=1.0)
    actor = ActorRuntime("local_player", position=Vec2(5, 5))
    actor.set_input(1, 0, False)
    for _ in range(180):
        actor.advance(1/60, lambda x, y: 0 < x < 24 and 0 < y < 18)
        runtime.tick(1/60)
    assert actor.position.x > 8.0 and actor.state.value == "walk"
    runtime.enter_space("observatory")
    assert state.last_room == "observatory"
    results["TEST_PLAYER_WALK_QUARTER"] = "PASS"

    # TEST_RAIN
    runtime.set_weather("rain")
    for _ in range(600): runtime.tick(1/60)
    assert state.weather == "rain"
    assert runtime.audio_mix()["rain"] > 0
    assert any(p.get("state") == "seek_shelter" for p in state.pet_states.values())
    assert any(n.get("state") in {"weather_response","shelter_pause","serve_shelter_crowd","inspect","leave","idle"} for n in state.npc_states.values())
    results["TEST_RAIN"] = "PASS"

    # TEST_DAY_NIGHT
    exposures=[]
    for minute in (360, 720, 1080, 1260, 180):
        runtime.time.minutes = minute
        runtime.tick(1/60)
        exposures.append(runtime.resolved_lighting().global_exposure)
    assert len(set(round(v, 3) for v in exposures)) >= 3
    results["TEST_DAY_NIGHT"] = "PASS"

    # TEST_TRANSITIONS
    for name in PROFILES:
        for _ in range(3):
            transition=SpaceTransitionOrchestrator(); transition.start("quarter","observatory",name)
            handoffs=0
            for _ in range(240):
                snap=transition.tick(1/120); handoffs += int(snap.handoff_ready)
                if snap.complete: break
            assert snap.complete and handoffs == 1 and not snap.movement_locked
    results["TEST_TRANSITIONS"] = "PASS"

    # TEST_INTERACTION
    system=InteractionSystem(); a=Target(1,0,2,"desk"); b=Target(1.1,.1,2,"chair")
    chosen=system.nearest([a,b],0,0,(1,0)); assert chosen in {a,b}
    for _ in range(10): assert system.nearest([a,b],.02,0,(1,0)) is chosen
    results["TEST_INTERACTION"] = "PASS"

    # TEST_SAVE_RELOAD / 0.4.1 migration
    import awake_world.world.save as save_module
    with tempfile.TemporaryDirectory(prefix="awake-gameplay-save-") as td:
        root=Path(td)
        old_save={"version":5,"last_room":"twin_core","world_minutes":1200,"weather":"cloudy","inventory":[],"npc_states":{}}
        save_module.SAVE_DIR=root; save_module.SAVE_FILE=root/"single_player_save.json"; save_module.BACKUP_FILE=root/"single_player_save.backup.json"; save_module.RECOVERY_FILE=root/"single_player_save.recovery.json"; save_module.CORRUPT_DIR=root/"corrupt"
        import json
        save_module.SAVE_FILE.write_text(json.dumps(old_save),encoding="utf-8")
        loaded=save_module.load_state(); assert loaded.schema_version==6 and loaded.last_room=="twin_core"
        loaded.flags.add("gameplay_test"); assert save_module.save_state(loaded)
        again=save_module.load_state(); assert "gameplay_test" in again.flags and again.schema_version==6
    results["TEST_SAVE_RELOAD"] = "PASS"

    return results


def main() -> int:
    results=run()
    for key,value in results.items(): print(f"{key}={value}")
    print("AWAKE_GAMEPLAY_TESTS_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
