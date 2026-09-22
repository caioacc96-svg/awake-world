from awake_world.presentation.camera_controller import CAMERA_PROFILES, CameraController
from awake_world.presentation.transition_orchestrator import SpaceTransitionOrchestrator, TransitionPhase


def test_camera_converges_without_overshoot():
    camera = CameraController(); p = CAMERA_PROFILES["indoor"]
    camera.snap(0, 0, 1.0)
    last = 0.0
    for _ in range(60):
        state = camera.update(1/60, 100, 0, 0, 0, p)
        assert state.x >= last
        assert state.x <= 100
        last = state.x
    assert state.x > 80


def test_transition_handoff_once_and_completes():
    t = SpaceTransitionOrchestrator(); t.start("quarter", "observatory", "exterior_to_interior")
    handoffs = 0
    for _ in range(120):
        s = t.tick(1/120)
        handoffs += int(s.handoff_ready)
    assert handoffs == 1
    assert s.phase == TransitionPhase.COMPLETE
    assert s.complete
