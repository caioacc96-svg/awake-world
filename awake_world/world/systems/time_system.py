from __future__ import annotations

from awake_world.world.systems.events import EventBus, WorldEvent

PHASE_ORDER = ("dawn", "day", "dusk", "night")
PHASE_STARTS = {
    "dawn": 5 * 60 + 30,
    "day": 8 * 60,
    "dusk": 17 * 60 + 30,
    "night": 20 * 60,
}


def phase_for_minutes(minutes: float) -> str:
    m = int(minutes) % (24 * 60)
    if PHASE_STARTS["dawn"] <= m < PHASE_STARTS["day"]:
        return "dawn"
    if PHASE_STARTS["day"] <= m < PHASE_STARTS["dusk"]:
        return "day"
    if PHASE_STARTS["dusk"] <= m < PHASE_STARTS["night"]:
        return "dusk"
    return "night"


class TimeSystem:
    """Pure simulation clock with EventBus publication and persistence sync."""

    def __init__(self, bus: EventBus, state, minutes_per_real_second: float = 0.5) -> None:
        self.bus = bus
        self.state = state
        self._minutes = float(state.world_minutes) % (24 * 60)
        self.minutes_per_real_second = float(minutes_per_real_second)
        self.paused = False

    @property
    def minutes(self) -> float:
        return self._minutes

    @minutes.setter
    def minutes(self, value: float) -> None:
        old_phase = self.phase
        self._minutes = float(value) % (24 * 60)
        self.state.world_minutes = self._minutes
        self.bus.publish(WorldEvent.TIME_CHANGED, minutes=self._minutes, phase=self.phase)
        if old_phase != self.phase and self.phase == "dusk":
            self.bus.publish(WorldEvent.SUNSET_STARTED, minutes=self._minutes)

    @property
    def phase(self) -> str:
        return phase_for_minutes(self._minutes)

    def advance(self, dt: float) -> tuple[bool, bool]:
        old_minute = int(self._minutes)
        old_phase = self.phase
        if not self.paused:
            self._minutes = (self._minutes + float(dt) * self.minutes_per_real_second) % (24 * 60)
        self.state.world_minutes = self._minutes
        minute_changed = int(self._minutes) != old_minute
        phase_changed = self.phase != old_phase
        if minute_changed or phase_changed:
            self.bus.publish(WorldEvent.TIME_CHANGED, minutes=self._minutes, phase=self.phase)
        if phase_changed and self.phase == "dusk":
            self.bus.publish(WorldEvent.SUNSET_STARTED, minutes=self._minutes)
        return minute_changed, phase_changed

    def jump_to_phase(self, phase: str) -> None:
        self.minutes = float(PHASE_STARTS[phase])

    def cycle_phase(self) -> str:
        current = self.phase
        index = PHASE_ORDER.index(current)
        target = PHASE_ORDER[(index + 1) % len(PHASE_ORDER)]
        self.jump_to_phase(target)
        return target
