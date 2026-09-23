from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HardeningBudget:
    max_dt: float = .05
    max_accumulator: float = 2.0
    ambient_divisor: int = 2
    pet_divisor: int = 2
    npc_sync_divisor: int = 6
    metrics_divisor: int = 30
    max_active_microevents: int = 2
    max_surface_occupants: int = 12


class HardeningSystem:
    """Deterministic update throttling and bounded-runtime safety contract."""

    def __init__(self, budget: HardeningBudget | None = None) -> None:
        self.budget = budget or HardeningBudget()
        self.fallback_count = 0

    def clamp_frame_dt(self, dt: float) -> float:
        value = float(dt)
        if value < 0.0:
            self.fallback_count += 1
            return 0.0
        if value > self.budget.max_dt:
            self.fallback_count += 1
        return min(value, self.budget.max_dt)

    @staticmethod
    def due(tick: int, divisor: int) -> bool:
        return divisor <= 1 or tick % divisor == 0

    def validate_counts(
        self,
        *,
        active_microevents: int,
        active_npcs: int,
        scene_objects: int = 0,
        max_active_npcs: int = 18,
        max_scene_objects: int = 1800,
    ) -> tuple[str, ...]:
        failures: list[str] = []
        if active_microevents > self.budget.max_active_microevents:
            failures.append("microevents")
        if active_npcs > max_active_npcs:
            failures.append("npcs")
        if scene_objects > max_scene_objects:
            failures.append("scene_objects")
        return tuple(failures)
