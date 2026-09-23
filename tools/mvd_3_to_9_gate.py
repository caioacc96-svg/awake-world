from __future__ import annotations

from awake_world.world.state import WorldState
from awake_world.world.systems.ambient_life import AmbientLifeSystem
from awake_world.world.systems.foundation_freeze import SPACES, FOUNDATION_GOLDEN_MATRIX, validate_foundation_matrix
from awake_world.world.systems.hardening import HardeningSystem
from awake_world.world.systems.interactions import InteractionSystem
from awake_world.world.systems.network_contracts import validate_multiplayer_ready_contract
from awake_world.world.systems.npc_system import ROUTINES
from awake_world.world.systems.release_candidate import evaluate_release_candidate
from awake_world.world.systems.subtle_life import SPACE_SUBTLE_LIFE_PROFILES, validate_subtle_life_contract
from awake_world.world.systems.surfaces import SURFACES
from awake_world.world.systems.traversal import TraversalSystem


def fail(gate: str, detail: str) -> None:
    raise SystemExit(f"{gate}_FAILED {detail}")


def main() -> int:
    if set(SPACE_SUBTLE_LIFE_PROFILES) != set(SPACES) or validate_subtle_life_contract():
        fail("AWAKE_MVD3_SUBTLE_LIFE", "profile_contract")
    for space_id in SPACES:
        ambient = AmbientLifeSystem(404)
        events = []
        for _ in range(30 * 60):
            events.extend(ambient.tick(1 / 60, space_id, "clear", 12 * 60))
        if not events or max(event.strength for event in events) > .82:
            fail("AWAKE_MVD3_SUBTLE_LIFE", f"{space_id}:idle_continuity")
    if len(ROUTINES) < 8:
        fail("AWAKE_MVD3_SUBTLE_LIFE", "purposeful_npc_routines")
    print("AWAKE_MVD3_SUBTLE_LIFE_OK")

    interaction = InteractionSystem()
    if interaction.switch_margin <= 0 or interaction.linger_multiplier <= 1:
        fail("AWAKE_MVD4_SPATIAL_INTERACTION", "target_retention")
    print("AWAKE_MVD4_SPATIAL_INTERACTION_OK")

    if validate_foundation_matrix() or len(FOUNDATION_GOLDEN_MATRIX) != 30:
        fail("AWAKE_MVD5_FOUNDATION_FREEZE", "golden_matrix")
    print("AWAKE_MVD5_FOUNDATION_FREEZE_OK")

    for space_id in SPACES:
        traversal = TraversalSystem(space_id)
        if traversal.raised_plane_count() < 1 or traversal.connector_count() < 1:
            fail("AWAKE_MVD6_MULTI_LEVEL_TRAVERSAL", space_id)
    print("AWAKE_MVD6_MULTI_LEVEL_TRAVERSAL_OK")

    if {surface.space_id for surface in SURFACES} != set(SPACES):
        fail("AWAKE_MVD7_SPATIAL_UTILITY", "surface_coverage")
    if validate_multiplayer_ready_contract():
        fail("AWAKE_MVD7_SPATIAL_UTILITY", "multiplayer_ready_contract")
    print("AWAKE_MVD7_SPATIAL_UTILITY_OK")

    hardening = HardeningSystem()
    if hardening.clamp_frame_dt(1.0) != hardening.budget.max_dt:
        fail("AWAKE_MVD8_PRODUCTION_HARDENING", "frame_bound")
    state = WorldState()
    from awake_world.world.systems.runtime import WorldRuntime
    left = WorldRuntime(state, minutes_per_real_second=1.0)
    right = WorldRuntime(WorldState(), minutes_per_real_second=1.0)
    for _ in range(60 * 90):
        left.tick(1 / 60)
        right.tick(1 / 60)
    if left.snapshot() != right.snapshot():
        fail("AWAKE_MVD8_PRODUCTION_HARDENING", "deterministic_soak")
    if len(left.microevents.active) > 2:
        fail("AWAKE_MVD8_PRODUCTION_HARDENING", "microevent_bound")

    import json
    import tempfile
    from pathlib import Path
    import awake_world.world.save as save_module
    with tempfile.TemporaryDirectory(prefix="awake-mvd8-stress-") as td:
        root = Path(td)
        save_module.SAVE_DIR = root
        save_module.SAVE_FILE = root / "single_player_save.json"
        save_module.BACKUP_FILE = root / "single_player_save.backup.json"
        save_module.RECOVERY_FILE = root / "single_player_save.recovery.json"
        save_module.CORRUPT_DIR = root / "corrupt"
        stress_state = WorldState()
        for index in range(24):
            stress_state.world_minutes = float((index * 71) % 1440)
            stress_state.flags.add(f"stress_{index}")
            if not save_module.save_state(stress_state):
                fail("AWAKE_MVD8_PRODUCTION_HARDENING", "save_write")
            loaded = save_module.load_state()
            if loaded.schema_version != stress_state.schema_version or f"stress_{index}" not in loaded.flags:
                fail("AWAKE_MVD8_PRODUCTION_HARDENING", "save_reload")
            stress_state = loaded
        json.dumps(left.snapshot(), sort_keys=True)
    print("AWAKE_MVD8_PRODUCTION_HARDENING_OK")

    readiness = evaluate_release_candidate(human_acceptance=False)
    if not readiness.technical_ready or readiness.failures:
        fail("AWAKE_MVD9_RELEASE_CANDIDATE", ",".join(readiness.failures))
    if readiness.releasable:
        fail("AWAKE_MVD9_RELEASE_CANDIDATE", "human_acceptance_must_remain_explicit")
    print("AWAKE_MVD9_RELEASE_CANDIDATE_OK")
    print("AWAKE_MVD3_TO_9_TECHNICAL_GATES_OK human_acceptance=PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
