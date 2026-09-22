from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TransitionPhase(StrEnum):
    IDLE = "idle"
    ACKNOWLEDGE = "acknowledge"
    DOOR = "door"
    CROSSFADE = "crossfade"
    HANDOFF = "handoff"
    SETTLE = "settle"
    COMPLETE = "complete"


@dataclass(frozen=True, slots=True)
class TransitionProfile:
    name: str
    total_ms: int
    handoff_ratio: float = 0.52
    movement_lock_ratio: float = 0.70
    camera_zoom_delta: float = 0.0
    audio_crossfade: float = 0.55


PROFILES: dict[str, TransitionProfile] = {
    "exterior_to_interior": TransitionProfile("exterior_to_interior", 820, 0.50, 0.74, 0.035, 0.62),
    "interior_to_exterior": TransitionProfile("interior_to_exterior", 760, 0.48, 0.68, -0.025, 0.58),
    "rooftop": TransitionProfile("rooftop", 940, 0.54, 0.72, -0.055, 0.70),
    "subterranean": TransitionProfile("subterranean", 1050, 0.55, 0.76, 0.040, 0.76),
    "garden": TransitionProfile("garden", 880, 0.50, 0.70, -0.020, 0.66),
    "laboratory": TransitionProfile("laboratory", 850, 0.52, 0.72, 0.020, 0.62),
    "social": TransitionProfile("social", 720, 0.48, 0.66, -0.015, 0.54),
}


@dataclass(slots=True)
class TransitionSnapshot:
    source: str = ""
    target: str = ""
    profile: str = "exterior_to_interior"
    elapsed_ms: float = 0.0
    progress: float = 0.0
    phase: TransitionPhase = TransitionPhase.IDLE
    handoff_ready: bool = False
    movement_locked: bool = False
    complete: bool = False


class SpaceTransitionOrchestrator:
    def __init__(self) -> None:
        self.snapshot = TransitionSnapshot()
        self._handoff_emitted = False

    def start(self, source: str, target: str, profile: str) -> TransitionSnapshot:
        if profile not in PROFILES:
            profile = "exterior_to_interior"
        self.snapshot = TransitionSnapshot(source=source, target=target, profile=profile, phase=TransitionPhase.ACKNOWLEDGE, movement_locked=True)
        self._handoff_emitted = False
        return self.snapshot

    def tick(self, dt: float) -> TransitionSnapshot:
        s = self.snapshot
        if s.phase in {TransitionPhase.IDLE, TransitionPhase.COMPLETE}:
            return s
        p = PROFILES[s.profile]
        s.elapsed_ms += max(0.0, dt) * 1000.0
        s.progress = min(1.0, s.elapsed_ms / p.total_ms)
        q = s.progress
        if q < 0.14:
            s.phase = TransitionPhase.ACKNOWLEDGE
        elif q < 0.34:
            s.phase = TransitionPhase.DOOR
        elif q < p.handoff_ratio:
            s.phase = TransitionPhase.CROSSFADE
        elif not self._handoff_emitted:
            s.phase = TransitionPhase.HANDOFF
            s.handoff_ready = True
            self._handoff_emitted = True
        elif q < 0.88:
            s.phase = TransitionPhase.SETTLE
            s.handoff_ready = False
        else:
            s.phase = TransitionPhase.SETTLE
        s.movement_locked = q < p.movement_lock_ratio
        if q >= 1.0:
            s.phase = TransitionPhase.COMPLETE
            s.complete = True
            s.movement_locked = False
            s.handoff_ready = False
        return s

    @property
    def active(self) -> bool:
        return self.snapshot.phase not in {TransitionPhase.IDLE, TransitionPhase.COMPLETE}
