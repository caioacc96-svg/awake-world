from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    metadata = {
        "build_version": version,
        "identity": "awake/world — THE LIVING NETWORK",
        "save_schema": 6,
        "simulation_hz": 60,
        "release_channel": "DEVELOPMENT" if version.endswith("-dev") else "GLOBAL",
        "commit": os.environ.get("GITHUB_SHA", git_value("rev-parse", "HEAD")),
        "ref": os.environ.get("GITHUB_REF_NAME", git_value("branch", "--show-current")),
        "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ci": bool(os.environ.get("GITHUB_ACTIONS")),
    }
    target = ROOT / "data" / "build.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"AWAKE_BUILD_METADATA_OK version={version} commit={metadata['commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
