from awake_world.simulation.actor_runtime import ActorRuntime, MovementConfig, Vec2


def free(_x: float, _y: float) -> bool:
    return True


def test_diagonal_is_normalized_and_accelerates():
    actor = ActorRuntime("player", position=Vec2(1, 1), config=MovementConfig(fixed_hz=60))
    actor.set_input(1, 1, False)
    for _ in range(30):
        actor.advance(1/60, free)
    assert abs(actor.desired_velocity.length() - actor.config.walk_speed) < 1e-6
    assert actor.velocity.length() > 2.0
    assert actor.state.value in {"walk", "turn"}


def test_actor_stops_precisely():
    actor = ActorRuntime("player", position=Vec2(), config=MovementConfig())
    actor.set_input(1, 0)
    for _ in range(60): actor.advance(1/60, free)
    actor.clear_input()
    for _ in range(60): actor.advance(1/60, free)
    assert actor.velocity.length() == 0.0
    assert actor.state.value == "idle"


def test_collision_slides_by_axis():
    actor = ActorRuntime("player", position=Vec2(0, 0))
    actor.set_input(1, 1)
    def collision(x: float, y: float) -> bool:
        return x < 0.03 or y > 0.0
    for _ in range(10): actor.advance(1/60, collision)
    assert actor.position.y > 0.0
