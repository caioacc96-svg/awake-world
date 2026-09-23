from __future__ import annotations

import ast
import json
import re
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"STATIC_VALIDATION_FAILED: {message}")


# Python syntax across the whole build.
for path in sorted(ROOT.rglob("*.py")):
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        fail(f"syntax error in {path.relative_to(ROOT)}: {exc}")

# Design tokens and QSS placeholders.
all_tokens: dict[str, object] = {}
for path in sorted((ROOT / "awake_world" / "design" / "tokens").glob("*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    overlap = all_tokens.keys() & data.keys()
    if overlap:
        fail(f"duplicate token(s): {sorted(overlap)}")
    all_tokens.update(data)

for qss in (ROOT / "awake_world" / "design" / "theme").glob("*.qss"):
    placeholders = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", qss.read_text(encoding="utf-8")))
    missing = placeholders - all_tokens.keys()
    if missing:
        fail(f"{qss.name} references missing tokens: {sorted(missing)}")

# Canonical discovery registry / rooms.
room_source = (ROOT / "awake_world" / "world" / "room.py").read_text(encoding="utf-8")
room_tree = ast.parse(room_source)
discoveries = None
rooms = None
for node in room_tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "DISCOVERY_KEYS":
                discoveries = ast.literal_eval(node.value)
            if isinstance(target, ast.Name) and target.id == "ROOM_TYPES":
                if not isinstance(node.value, ast.Dict):
                    fail("ROOM_TYPES is not a dict")
                rooms = {ast.literal_eval(k) for k in node.value.keys}

if discoveries is None or len(discoveries) != 29:
    fail(f"expected 29 discoveries, got {0 if discoveries is None else len(discoveries)}")
if rooms != {"headquarters", "plaza", "rooftop", "home"}:
    fail(f"unexpected room registry: {rooms}")

# Progression catalog must contain the authored home objects.
prog_source = (ROOT / "awake_world" / "world" / "progression.py").read_text(encoding="utf-8")
for decor_key in (
    "memory_plant", "signal_lamp", "woven_rug", "record_console", "portal_sculpture", "garden_stone"
):
    if decor_key not in prog_source:
        fail(f"missing decor catalog entry: {decor_key}")

# Audio assets are deliberately plain WAV so no codec/runtime plugin is required.
audio_dir = ROOT / "awake_world" / "assets" / "audio"
required_audio = {
    "hq_day.wav", "hq_night.wav", "plaza_day.wav", "plaza_night.wav",
    "rooftop_day.wav", "rooftop_night.wav", "home_day.wav", "home_night.wav",
    "interact.wav", "discover.wav",
}
actual_audio = {p.name for p in audio_dir.glob("*.wav")}
missing_audio = required_audio - actual_audio
if missing_audio:
    fail(f"missing audio assets: {sorted(missing_audio)}")
for name in required_audio:
    try:
        with wave.open(str(audio_dir / name), "rb") as wav:
            if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() != 22050:
                fail(f"unexpected WAV format: {name}")
            if wav.getnframes() <= 0:
                fail(f"empty WAV: {name}")
    except wave.Error as exc:
        fail(f"invalid WAV {name}: {exc}")

# 0.5 baseline architecture and the canonical experience contract must remain present in 0.6.
for relative in (
    "awake_world/world/state.py",
    "awake_world/world/district.py",
    "awake_world/world/environment.py",
    "awake_world/world/systems/events.py",
    "awake_world/world/systems/runtime.py",
    "awake_world/world/systems/weather.py",
    "awake_world/world/systems/spaces.py",
    "awake_world/world/systems/presence.py",
    "awake_world/world/systems/microevents.py",
    "awake_world/world/systems/time_system.py",
    "awake_world/world/systems/audio_zones.py",
    "awake_world/world/systems/interactions.py",
    "awake_world/world/systems/lighting_system.py",
    "awake_world/world/systems/npc_system.py",
    "awake_world/world/systems/performance.py",
    "awake_world/world/systems/ambient_life.py",
    "awake_world/world/systems/diagnostics.py",
    "awake_world/world/systems/pets.py",
    "awake_world/world/systems/subtle_life.py",
    "awake_world/world/systems/traversal.py",
    "awake_world/world/systems/surfaces.py",
    "awake_world/world/systems/foundation_freeze.py",
    "awake_world/world/systems/hardening.py",
    "awake_world/world/systems/network_contracts.py",
    "awake_world/world/systems/release_candidate.py",
    "awake_world/simulation/actor_runtime.py",
    "awake_world/simulation/replay.py",
    "awake_world/presentation/camera_controller.py",
    "awake_world/presentation/transition_orchestrator.py",
    "docs/AWAKE_WORLD_INTERACTION_EXPERIENCE_BIBLE_v1.md",
    ".github/workflows/ci.yml",
    ".github/workflows/update-goldens.yml",
    ".github/workflows/release.yml",
    "awake_world.spec",
    "tools/deterministic_replay_test.py",
    "tools/gameplay_tests.py",
    "tools/mvd_3_to_9_gate.py",
    "tools/living_cast_gate.py",
    "tools/render_living_cast.py",
    "docs/AWAKE_WORLD_07_CHARACTER_SPRITE_BIBLE.md",
    "awake_world/design/characters.py",
    "tools/render_golden_scenes.py",
    "tools/package_windows.py",
    "tools/write_build_metadata.py",
):
    if not (ROOT / relative).exists():
        fail(f"missing living-city system: {relative}")

space_source = (ROOT / "awake_world" / "world" / "systems" / "spaces.py").read_text(encoding="utf-8")
for space_id in ("quarter","central_plaza","observatory","grid","twin_core","trinity_lab","garage","kawaii_garden","pit","glasshouse"):
    if f'"{space_id}"' not in space_source:
        fail(f"missing Awake Quarter space definition: {space_id}")


# Frozen 0.5 invariants inherited by the 0.6 development line.
version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if not re.fullmatch(r"0\.(?:5|6|7)\.\d+(?:-dev)?", version):
    fail(f"unexpected Awake World version: {version}")

state_source = (ROOT / "awake_world" / "world" / "state.py").read_text(encoding="utf-8")
if "schema_version: int = 6" not in state_source:
    fail("WorldState schema 6 missing")

if version.startswith("0.7."):
    init_source = (ROOT / "awake_world" / "__init__.py").read_text(encoding="utf-8")
    if '__version__ = "0.7.0-dev"' not in init_source:
        fail("0.7 package version mismatch")
    if 'build_version: str = "0.7.0-dev"' not in state_source:
        fail("0.7 WorldState build version mismatch")
    cast_source = (ROOT / "awake_world" / "design" / "characters.py").read_text(encoding="utf-8")
    if "CAIO_MONKS" not in cast_source or "DIRECTIONS" not in cast_source:
        fail("0.7 Living Cast profile contract missing")

runtime_source = (ROOT / "awake_world" / "world" / "systems" / "runtime.py").read_text(encoding="utf-8")
if "FIXED_HZ = 60" not in runtime_source:
    fail("fixed-step 60 Hz runtime missing")

ci_source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
for gate in ("fast-linux", "windows-qt", "Packaged executable smoke", "Render deterministic golden scenes"):
    if gate not in ci_source:
        fail(f"CI gate missing: {gate}")

bible = (ROOT / "docs" / "AWAKE_WORLD_INTERACTION_EXPERIENCE_BIBLE_v1.md").read_text(encoding="utf-8")
for law in ("THE SPACE IS THE INTERFACE", "SUBTLE LIFE", "PERCEIVED COMPLEXITY > RAW COMPLEXITY"):
    if law not in bible:
        fail(f"canonical experience law missing: {law}")

required = [
    "run.py",
    "launch_awake.py",
    "RUN_AWAKE_WORLD.cmd",
    "start_awake.cmd",
    "start_awake.ps1",
    "smoke_test.ps1",
    "verify_awake.cmd",
    "tools/core_test.py",
    "requirements.txt",
    "awake_world/world/audio.py",
    "awake_world/world/npc.py",
    "awake_world/world/progression.py",
    "awake_world/world/lighting.py",
    "awake_world/world/room.py",
    "awake_world/ui/main_window.py",
]
for relative in required:
    if not (ROOT / relative).exists():
        fail(f"missing required file: {relative}")

print("AWAKE_STATIC_OK")
print(f"tokens={len(all_tokens)} discoveries={len(discoveries)} legacy_rooms={len(rooms)} quarter_spaces=10 audio={len(required_audio)} schema=6 fixed_hz=60")
