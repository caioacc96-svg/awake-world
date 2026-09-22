from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import sys
import zipfile
from typing import Any


class DiagnosticsSystem:
    def __init__(self, root: Path | None = None, ring_size: int = 240) -> None:
        default = Path(os.environ.get("AWAKE_DIAGNOSTICS_DIR", str(Path.home() / ".awake_world" / "diagnostics")))
        self.root = root or default
        self.events: deque[dict[str, Any]] = deque(maxlen=ring_size)
        self.inputs: deque[dict[str, Any]] = deque(maxlen=ring_size)

    def event(self, category: str, **payload: Any) -> None:
        self.events.append({"ts": datetime.now(timezone.utc).isoformat(), "category": category, **payload})

    def input(self, **payload: Any) -> None:
        self.inputs.append({"ts": datetime.now(timezone.utc).isoformat(), **payload})

    def export(
        self,
        build: dict[str, Any],
        world_state: dict[str, Any],
        performance: dict[str, Any],
        runtime_log: str = "",
        crash_log: str = "",
        replay: dict[str, Any] | None = None,
    ) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        payloads = {
            "build.json": build,
            "system.json": {"python": sys.version, "platform": platform.platform(), "machine": platform.machine()},
            "world_state_snapshot.json": world_state,
            "performance_snapshot.json": performance,
            "last_events.json": list(self.events),
            "last_inputs.json": list(self.inputs),
        }
        if replay is not None:
            payloads["simulation_replay.json"] = replay
        for name, value in payloads.items():
            (self.root / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        (self.root / "runtime.log").write_text(runtime_log, encoding="utf-8")
        (self.root / "crash.log").write_text(crash_log, encoding="utf-8")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.root.parent / f"awake_diagnostics_{stamp}.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in (*payloads.keys(), "runtime.log", "crash.log"):
                zf.write(self.root / name, arcname=f"diagnostics/{name}")
        return target
