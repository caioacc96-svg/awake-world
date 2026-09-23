from __future__ import annotations

from dataclasses import dataclass

from awake_world.world.state import WorldState
from awake_world.world.systems.ambient_life import AmbientLifeSystem
from awake_world.world.systems.foundation_freeze import SPACES, FOUNDATION_GOLDEN_MATRIX, validate_foundation_matrix
from awake_world.world.systems.hardening import HardeningSystem
from awake_world.world.systems.interactions import InteractionSystem
from awake_world.world.systems.network_contracts import (
    AvatarReplicationState,
    RealtimeCapabilities,
    ReplicationEnvelope,
    validate_multiplayer_ready_contract,
)
from awake_world.world.systems.npc_system import NPCSystem, ROUTINES
from awake_world.world.systems.release_candidate import evaluate_release_candidate
from awake_world.world.systems.subtle_life import SPACE_SUBTLE_LIFE_PROFILES, validate_subtle_life_contract
from awake_world.world.systems.surfaces import SURFACES, SurfaceOccupancySystem, surfaces_for_space
from awake_world.world.systems.traversal import TraversalSystem


@dataclass(frozen=True)
class Target:
    x: float
    y: float
    radius: float
    key: str
    z: float = 0.0
    priority: float = 0.0


def test_mvd3_profiles_cover_all_spaces_and_are_bounded() -> None:
    assert set(SPACE_SUBTLE_LIFE_PROFILES) == set(SPACES)
    assert validate_subtle_life_contract() == ()
    for profile in SPACE_SUBTLE_LIFE_PROFILES.values():
        assert profile.vegetation_amplitude_deg <= 1.85
        assert profile.occupancy_traces
        assert profile.state_anchors


def test_mvd3_ambient_life_is_seeded_sparse_and_continuous() -> None:
    a = AmbientLifeSystem(404)
    b = AmbientLifeSystem(404)
    out_a = []
    out_b = []
    for _ in range(30 * 60):
        out_a.extend(a.tick(1 / 60, "kawaii_garden", "rain", 14 * 60))
        out_b.extend(b.tick(1 / 60, "kawaii_garden", "rain", 14 * 60))
    assert out_a == out_b
    assert 3 <= len(out_a) <= 12
    assert all(.08 <= event.strength <= .82 for event in out_a)


def test_mvd3_npcs_have_authored_purpose_across_world() -> None:
    covered = {entry.space_id for routine in ROUTINES.values() for entry in routine.schedule}
    assert set(SPACES) - {"kawaii_garden"} <= covered
    snapshots = NPCSystem(404).snapshots(14 * 60, "clear", "twin_core")
    assert snapshots["developer"]["space_id"] == "twin_core"
    assert snapshots["developer"]["state"] in {"hardware_test", "build_review", "pair_session", "lunch"}


def test_mvd4_interaction_height_and_hysteresis() -> None:
    system = InteractionSystem(switch_margin=.18)
    low = Target(1.0, 0.0, 2.0, "low", z=0.0, priority=.4)
    high = Target(1.0, .02, 2.0, "high", z=.8, priority=1.0)
    chosen = system.nearest([low, high], 0.0, 0.0, (1.0, 0.0), actor_z=0.0)
    assert chosen is low
    for _ in range(8):
        assert system.nearest([low, high], .02, 0.0, (1.0, 0.0), actor_z=0.0) is low


def test_mvd5_foundation_matrix_covers_10_spaces_and_three_frames() -> None:
    assert validate_foundation_matrix() == ()
    assert len(FOUNDATION_GOLDEN_MATRIX) == 30
    assert {row.space_id for row in FOUNDATION_GOLDEN_MATRIX} == set(SPACES)


def test_mvd6_every_space_has_authored_elevation_and_connector() -> None:
    for space_id in SPACES:
        traversal = TraversalSystem(space_id)
        assert traversal.raised_plane_count() >= 1
        assert traversal.connector_count() >= 1
        stair = traversal.profile.stairs[0]
        high = traversal._stair_sample(stair, stair.x, stair.y)
        assert high is not None and high.connector and high.elevation > 0
        plane = traversal.profile.planes[0]
        sample = traversal.sample(plane.x + plane.w * .5, plane.y + plane.d * .5)
        assert sample.elevation >= plane.h


def test_mvd6_rejects_unconnected_large_vertical_jump() -> None:
    traversal = TraversalSystem("observatory")
    plane = traversal.profile.planes[0]
    tx = plane.x + plane.w * .5
    ty = plane.y + plane.d * .5
    assert traversal.elevation_at(tx, ty) >= .30
    assert not traversal.can_transition(.5, .5, 0.0, tx, ty)


def test_mvd7_surface_contract_and_capacity() -> None:
    assert {surface.space_id for surface in SURFACES} == set(SPACES)
    assert {"desk", "project_board", "meeting_table", "lab_workbench", "sofa", "arcade"} <= {s.kind for s in SURFACES}
    state = WorldState()
    occupancy = SurfaceOccupancySystem(state)
    surface = next(s for s in SURFACES if s.id == "observatory.desk")
    assert occupancy.occupy(surface, "local_player")
    assert not occupancy.occupy(surface, "second_member")
    occupancy.release(surface, "local_player")
    assert occupancy.occupy(surface, "second_member")
    assert surfaces_for_space("twin_core")


def test_mvd7_multiplayer_ready_contract_is_explicit_and_serializable() -> None:
    assert validate_multiplayer_ready_contract() == ()
    capabilities = RealtimeCapabilities()
    assert capabilities.voice_ready and capabilities.video_ready and capabilities.screen_share_ready
    state = AvatarReplicationState("member", "observatory", 1.0, 2.0, .3, 0.0, -1.0, "walk", 7)
    wire = ReplicationEnvelope.from_state("avatar", 7, state).to_wire()
    assert wire["kind"] == "avatar"
    assert wire["payload"]["elevation"] == .3


def test_mvd8_hardening_is_bounded_and_deterministic() -> None:
    hardening = HardeningSystem()
    assert hardening.clamp_frame_dt(-1) == 0
    assert hardening.clamp_frame_dt(1.0) == hardening.budget.max_dt
    assert hardening.due(12, 6)
    assert not hardening.due(13, 6)
    assert hardening.validate_counts(active_microevents=2, active_npcs=10) == ()


def test_mvd9_release_candidate_separates_technical_and_human_acceptance() -> None:
    readiness = evaluate_release_candidate(human_acceptance=False)
    assert readiness.technical_ready
    assert not readiness.human_acceptance
    assert not readiness.releasable
    accepted = evaluate_release_candidate(human_acceptance=True)
    assert accepted.releasable
