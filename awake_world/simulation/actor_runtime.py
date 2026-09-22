from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math
from typing import Callable


@dataclass(slots=True)
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vec2":
        n = self.length()
        if n <= 1e-9:
            return Vec2()
        return Vec2(self.x / n, self.y / n)

    def dot(self, other: "Vec2") -> float:
        return self.x * other.x + self.y * other.y


class ActorKind(StrEnum):
    PLAYER = "player"
    NPC = "npc"
    PET = "pet"


class ActorMotionState(StrEnum):
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    TURN = "turn"
    INTERACT = "interact"
    SIT = "sit"
    OBSERVE = "observe"
    USE_OBJECT = "use_object"
    CONTEXT = "context"


@dataclass(frozen=True, slots=True)
class MovementConfig:
    walk_speed: float = 3.35
    run_speed: float = 4.86
    acceleration_time: float = 0.18
    deceleration_time: float = 0.21
    reversal_brake_multiplier: float = 1.45
    stop_epsilon: float = 0.025
    fixed_hz: int = 60
    max_substeps: int = 5

    @property
    def fixed_dt(self) -> float:
        return 1.0 / max(1, self.fixed_hz)


class ActorRuntime:
    """Renderer-agnostic actor locomotion with fixed-step simulation."""

    def __init__(
        self,
        actor_id: str,
        kind: ActorKind = ActorKind.PLAYER,
        position: Vec2 | None = None,
        config: MovementConfig | None = None,
    ) -> None:
        self.actor_id = actor_id
        self.kind = kind
        self.config = config or MovementConfig()
        self.position = position or Vec2()
        self.previous_position = Vec2(self.position.x, self.position.y)
        self.velocity = Vec2()
        self.desired_velocity = Vec2()
        self.input_direction = Vec2()
        self.facing = Vec2(0.0, 1.0)
        self.state = ActorMotionState.IDLE
        self.running = False
        self.run_blend = 0.0
        self._accumulator = 0.0
        self.tick_index = 0

    def teleport(self, x: float, y: float) -> None:
        self.position = Vec2(float(x), float(y))
        self.previous_position = Vec2(float(x), float(y))
        self.velocity = Vec2()
        self.desired_velocity = Vec2()
        self._accumulator = 0.0

    def set_input(self, x: float, y: float, running: bool = False) -> None:
        direction = Vec2(float(x), float(y)).normalized()
        self.input_direction = direction
        self.running = bool(running)
        speed = self.config.run_speed if self.running else self.config.walk_speed
        self.desired_velocity = Vec2(direction.x * speed, direction.y * speed)
        if direction.length() > 0.0:
            self.facing = direction

    def clear_input(self) -> None:
        self.set_input(0.0, 0.0, False)

    @staticmethod
    def _move_towards(current: float, target: float, max_delta: float) -> float:
        delta = target - current
        if abs(delta) <= max_delta:
            return target
        return current + math.copysign(max_delta, delta)

    def advance(self, dt: float, can_move_to: Callable[[float, float], bool]) -> int:
        """Advance using fixed ticks. Returns number of simulation steps executed."""
        self._accumulator = min(self._accumulator + max(0.0, float(dt)), self.config.fixed_dt * self.config.max_substeps)
        steps = 0
        while self._accumulator + 1e-12 >= self.config.fixed_dt and steps < self.config.max_substeps:
            self._fixed_step(self.config.fixed_dt, can_move_to)
            self._accumulator -= self.config.fixed_dt
            steps += 1
        return steps

    @property
    def interpolation_alpha(self) -> float:
        return max(0.0, min(1.0, self._accumulator / self.config.fixed_dt))

    def interpolated_position(self) -> Vec2:
        a = self.interpolation_alpha
        return Vec2(
            self.previous_position.x + (self.position.x - self.previous_position.x) * a,
            self.previous_position.y + (self.position.y - self.previous_position.y) * a,
        )

    def _fixed_step(self, dt: float, can_move_to: Callable[[float, float], bool]) -> None:
        self.previous_position = Vec2(self.position.x, self.position.y)
        desired_speed = self.desired_velocity.length()
        current_speed = self.velocity.length()
        reversing = current_speed > 0.05 and desired_speed > 0.05 and self.velocity.dot(self.desired_velocity) < 0.0

        if desired_speed > current_speed:
            time_to_target = max(0.01, self.config.acceleration_time)
            accel = max(self.config.walk_speed, desired_speed) / time_to_target
        else:
            time_to_target = max(0.01, self.config.deceleration_time)
            accel = max(self.config.walk_speed, current_speed) / time_to_target
        if reversing:
            accel *= self.config.reversal_brake_multiplier

        max_delta = accel * dt
        self.velocity.x = self._move_towards(self.velocity.x, self.desired_velocity.x, max_delta)
        self.velocity.y = self._move_towards(self.velocity.y, self.desired_velocity.y, max_delta)

        if desired_speed <= 1e-9 and self.velocity.length() < self.config.stop_epsilon:
            self.velocity = Vec2()

        nx = self.position.x + self.velocity.x * dt
        ny = self.position.y + self.velocity.y * dt
        moved_x = can_move_to(nx, self.position.y)
        if moved_x:
            self.position.x = nx
        else:
            self.velocity.x = 0.0
        moved_y = can_move_to(self.position.x, ny)
        if moved_y:
            self.position.y = ny
        else:
            self.velocity.y = 0.0

        speed = self.velocity.length()
        target_blend = 1.0 if self.running and desired_speed > 0.0 else 0.0
        blend_rate = min(1.0, dt / 0.18)
        self.run_blend += (target_blend - self.run_blend) * blend_rate

        if speed <= self.config.stop_epsilon:
            self.state = ActorMotionState.IDLE
        elif reversing:
            self.state = ActorMotionState.TURN
        elif self.running or self.run_blend > 0.55:
            self.state = ActorMotionState.RUN
        else:
            self.state = ActorMotionState.WALK
        self.tick_index += 1

    def snapshot(self) -> dict[str, object]:
        return {
            "actor_id": self.actor_id,
            "kind": self.kind.value,
            "tick": self.tick_index,
            "position": [round(self.position.x, 6), round(self.position.y, 6)],
            "velocity": [round(self.velocity.x, 6), round(self.velocity.y, 6)],
            "desired_velocity": [round(self.desired_velocity.x, 6), round(self.desired_velocity.y, 6)],
            "facing": [round(self.facing.x, 6), round(self.facing.y, 6)],
            "state": self.state.value,
            "running": self.running,
            "run_blend": round(self.run_blend, 6),
        }
