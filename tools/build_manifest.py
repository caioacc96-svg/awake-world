from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__", "build", "dist", "release", "diagnostics", "visual_output"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if relative.parts[:3] == ("awake_world", "assets", "audio") and path.suffix.lower() == ".wav":
        return False
    return path.name != "BUILD_MANIFEST.json"


def build_manifest() -> dict[str, object]:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files: list[dict[str, object]] = []
    for path in sorted(p for p in ROOT.rglob("*") if p.is_file() and included(p)):
        relative = path.relative_to(ROOT).as_posix()
        files.append({"path": relative, "size": path.stat().st_size, "sha256": sha256(path)})
    return {
        "build": version,
        "name": "Awake World — 0.5 GLOBAL",
        "identity": "awake/world — THE LIVING NETWORK",
        "canonical_windows_entry": "AWAKE_WORLD.exe",
        "save_schema": 6,
        "simulation_hz": 60,
        "python_min": "3.11",
        "pyside6": "6.11.2",
        "validation": {
            "static": "CI_REQUIRED",
            "type": "CI_REQUIRED",
            "unit": "CI_REQUIRED",
            "simulation": "CI_REQUIRED",
            "save": "CI_REQUIRED",
            "npc": "CI_REQUIRED",
            "interaction": "CI_REQUIRED",
            "space": "CI_REQUIRED",
            "weather": "CI_REQUIRED",
            "visual": "WINDOWS_CI_REQUIRED",
            "windows_qt": "WINDOWS_CI_REQUIRED",
            "package": "WINDOWS_CI_REQUIRED",
            "packaged_smoke": "WINDOWS_CI_REQUIRED",
        },
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest()
    target = ROOT / "BUILD_MANIFEST.json"
    rendered = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != rendered:
            raise SystemExit("BUILD_MANIFEST_OUT_OF_DATE")
        print("AWAKE_MANIFEST_OK")
        return 0
    target.write_text(rendered, encoding="utf-8")
    print(f"AWAKE_MANIFEST_WRITTEN files={len(manifest['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
