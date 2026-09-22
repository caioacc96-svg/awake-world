from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable


@dataclass(slots=True)
class RecordedFrame:
    tick: int
    input: dict[str, Any]
    actor_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    world_events: list[dict[str, Any]] = field(default_factory=list)
    transitions: list[dict[str, Any]] = field(default_factory=list)


class SimulationRecorder:
    def __init__(self, seed: int, max_frames: int = 7200) -> None:
        self.seed = int(seed)
        self.frames: deque[RecordedFrame] = deque(maxlen=max(1, int(max_frames)))

    def record(
        self,
        tick: int,
        input_state: dict[str, Any],
        actor_states: dict[str, dict[str, Any]] | None = None,
        world_events: Iterable[dict[str, Any]] = (),
        transitions: Iterable[dict[str, Any]] = (),
    ) -> None:
        self.frames.append(RecordedFrame(
            int(tick), dict(input_state), dict(actor_states or {}), list(world_events), list(transitions)
        ))

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": "awake-sim-replay-v1",
            "seed": self.seed,
            "frames": [
                {
                    "tick": f.tick,
                    "input": f.input,
                    "actor_states": f.actor_states,
                    "world_events": f.world_events,
                    "transitions": f.transitions,
                }
                for f in self.frames
            ],
        }

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


class SimulationReplay:
    def __init__(self, data: dict[str, Any]) -> None:
        if data.get("format") != "awake-sim-replay-v1":
            raise ValueError("Unsupported replay format")
        self.seed = int(data.get("seed", 0))
        self.frames = list(data.get("frames", []))
        self.index = 0

    @classmethod
    def read(cls, path: Path) -> "SimulationReplay":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def next_frame(self) -> dict[str, Any] | None:
        if self.index >= len(self.frames):
            return None
        frame = self.frames[self.index]
        self.index += 1
        return frame

    def reset(self) -> None:
        self.index = 0
