from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PerformanceBudget:
    target_fps: int = 60
    frame_ms: float = 16.67
    simulation_ms: float = 4.0
    render_ms: float = 11.5
    ram_mb: int = 900
    max_scene_objects: int = 1800
    max_active_npcs: int = 18
    max_dynamic_lights: int = 10
    max_audio_sources: int = 20
    max_rain_streaks: int = 64
    max_event_throughput_s: int = 60


class PerformanceSystem:
    def __init__(self, budget: PerformanceBudget | None = None) -> None:
        self.budget = budget or PerformanceBudget()

    @staticmethod
    def simulation_lod(distance_tiles: float) -> str:
        if distance_tiles < 12: return "full"
        if distance_tiles < 32: return "reduced"
        if distance_tiles < 80: return "logical_only"
        return "sleep"
