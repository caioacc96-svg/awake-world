from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__", "build", "dist", "release", "diagnostics", "visual_output"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
TEXT_SUFFIXES = {
    ".cfg", ".cmd", ".css", ".html", ".ini", ".js", ".json", ".md", ".ps1",
    ".py", ".qss", ".spec", ".toml", ".ts", ".txt", ".xml", ".yaml", ".yml",
}
TEXT_NAMES = {"VERSION", ".gitignore", ".gitattributes"}


def canonical_bytes(path: Path) -> bytes:
    payload = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES:
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return payload


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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
        payload = canonical_bytes(path)
        files.append({"path": relative, "size": len(payload), "sha256": sha256_bytes(payload)})
    return {
        "build": version,
        "name": f"Awake World — {version}",
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


def manifest_delta(existing: dict[str, object], generated: dict[str, object]) -> dict[str, object]:
    old_files = {
        str(item["path"]): item
        for item in existing.get("files", [])
        if isinstance(item, dict) and "path" in item
    }
    new_files = {
        str(item["path"]): item
        for item in generated.get("files", [])
        if isinstance(item, dict) and "path" in item
    }
    missing = sorted(path for path in new_files if path not in old_files)
    extra = sorted(path for path in old_files if path not in new_files)
    changed = []
    for path in sorted(old_files.keys() & new_files.keys()):
        old = old_files[path]
        new = new_files[path]
        if old.get("size") != new.get("size") or old.get("sha256") != new.get("sha256"):
            changed.append({
                "path": path,
                "old_size": old.get("size"),
                "new_size": new.get("size"),
                "old_sha256": old.get("sha256"),
                "new_sha256": new.get("sha256"),
            })
    metadata = {
        key: {"old": existing.get(key), "new": generated.get(key)}
        for key in generated
        if key != "files" and existing.get(key) != generated.get(key)
    }
    return {"missing": missing, "extra": extra, "changed": changed, "metadata": metadata}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest()
    target = ROOT / "BUILD_MANIFEST.json"
    rendered = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not target.exists():
            raise SystemExit("BUILD_MANIFEST_MISSING")
        current_text = target.read_text(encoding="utf-8")
        if current_text != rendered:
            try:
                current = json.loads(current_text)
                delta = manifest_delta(current, manifest)
                print("BUILD_MANIFEST_DELTA")
                print(json.dumps(delta, indent=2, ensure_ascii=False))
            except (json.JSONDecodeError, TypeError, KeyError) as exc:
                print(f"BUILD_MANIFEST_PARSE_ERROR: {exc}")
            raise SystemExit("BUILD_MANIFEST_OUT_OF_DATE")
        print("AWAKE_MANIFEST_OK")
        return 0
    target.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"AWAKE_MANIFEST_WRITTEN files={len(manifest['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
