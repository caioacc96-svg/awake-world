from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
from typing import Any

from awake_world.world.state import WorldState
from awake_world.world.progression import STARTER_DECOR


CURRENT_SAVE_SCHEMA = 6
SAVE_DIR = Path(os.environ.get("AWAKE_SAVE_DIR", str(Path.home() / ".awake_world")))
SAVE_FILE = SAVE_DIR / "single_player_save.json"
BACKUP_FILE = SAVE_DIR / "single_player_save.backup.json"
RECOVERY_FILE = SAVE_DIR / "single_player_save.recovery.json"
CORRUPT_DIR = SAVE_DIR / "corrupt"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _coerce_weather(value: object) -> str:
    weather = str(value or "clear").lower()
    return weather if weather in {"clear", "cloudy", "rain"} else "clear"


def migrate_payload(data: dict[str, Any]) -> dict[str, Any]:
    migrated = dict(data)
    # 0.4.1 wrote `version: 5`. Some early saves may omit it; treat those as v5.
    schema = int(migrated.get("schema_version", migrated.get("version", 5)))
    if schema > CURRENT_SAVE_SCHEMA:
        raise ValueError(f"save schema {schema} is newer than supported {CURRENT_SAVE_SCHEMA}")
    if schema <= 5:
        migrated.setdefault("world_seed", 404)
        migrated.setdefault("district_states", {})
        migrated.setdefault("pet_states", {})
        migrated.setdefault("environment_state", {})
        migrated.setdefault("player_state", {})
        migrated["schema_version"] = 6
    migrated.setdefault("build_version", "0.4.1-migrated")
    migrated["schema_version"] = CURRENT_SAVE_SCHEMA
    return migrated


def _state_from_payload(raw: dict[str, Any]) -> WorldState:
    data = migrate_payload(raw)
    inventory = {str(x) for x in data.get("inventory", [])} | set(STARTER_DECOR)
    journal = [str(x) for x in data.get("journal", ["arrival"])]
    if "arrival" not in journal:
        journal.insert(0, "arrival")
    return WorldState(
        schema_version=CURRENT_SAVE_SCHEMA,
        build_version=str(data.get("build_version", "0.5.0-dev")),
        world_seed=int(data.get("world_seed", 404)),
        discovered={str(x) for x in data.get("discovered", [])},
        toggles={str(k): bool(v) for k, v in data.get("toggles", {}).items()},
        visits={str(k): int(v) for k, v in data.get("visits", {}).items()},
        world_minutes=float(data.get("world_minutes", 8 * 60 + 24)),
        inventory=inventory,
        decor={str(k): str(v) for k, v in data.get("decor", {}).items()},
        flags={str(x) for x in data.get("flags", [])},
        conversations={str(k): int(v) for k, v in data.get("conversations", {}).items()},
        journal=journal,
        last_room=str(data.get("last_room", "quarter")),
        weather=_coerce_weather(data.get("weather")),
        weather_intensity=float(data.get("weather_intensity", 0.0)),
        active_events={str(k): float(v) for k, v in data.get("active_events", {}).items()},
        district_states={str(k): dict(v) for k, v in data.get("district_states", {}).items()},
        space_states={str(k): dict(v) for k, v in data.get("space_states", {}).items()},
        npc_states={str(k): dict(v) for k, v in data.get("npc_states", {}).items()},
        pet_states={str(k): dict(v) for k, v in data.get("pet_states", {}).items()},
        presence={str(k): dict(v) for k, v in data.get("presence", {}).items()},
        environment_state=dict(data.get("environment_state", {})),
        player_state=dict(data.get("player", data.get("player_state", {}))),
    )


def _read_candidate(path: Path) -> WorldState | None:
    if not path.exists():
        return None
    try:
        return _state_from_payload(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None


def load_state() -> WorldState:
    state = _read_candidate(SAVE_FILE)
    if state is not None:
        return state
    # Automatic recovery path; preserve corrupt primary for diagnostics.
    if SAVE_FILE.exists():
        try:
            CORRUPT_DIR.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(SAVE_FILE, CORRUPT_DIR / f"single_player_save_{stamp}.json")
        except OSError:
            pass
    for candidate in (RECOVERY_FILE, BACKUP_FILE):
        state = _read_candidate(candidate)
        if state is not None:
            return state
    return WorldState()


def state_payload(state: WorldState) -> dict[str, Any]:
    return {
        "schema_version": CURRENT_SAVE_SCHEMA,
        "build_version": state.build_version,
        "timestamp": _timestamp(),
        "world_seed": int(state.world_seed),
        "world_minutes": round(float(state.world_minutes), 4),
        "weather": state.weather,
        "weather_intensity": round(float(state.weather_intensity), 4),
        "district_states": state.district_states,
        "space_states": state.space_states,
        "player": state.player_state,
        "npc_states": state.npc_states,
        "pet_states": state.pet_states,
        "presence": state.presence,
        "active_events": state.active_events,
        "environment_state": state.environment_state,
        # Legacy/progression fields retained for 0.4.1 continuity.
        "discovered": sorted(state.discovered),
        "toggles": state.toggles,
        "visits": state.visits,
        "inventory": sorted(state.inventory),
        "decor": state.decor,
        "flags": sorted(state.flags),
        "conversations": state.conversations,
        "journal": state.journal,
        "last_room": state.last_room,
    }


def save_state(state: WorldState) -> bool:
    try:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        payload_text = json.dumps(state_payload(state), indent=2, ensure_ascii=False, sort_keys=True)
        tmp = SAVE_FILE.with_suffix(".tmp")
        tmp.write_text(payload_text, encoding="utf-8")
        # Verify before replacing the canonical save.
        _state_from_payload(json.loads(tmp.read_text(encoding="utf-8")))
        if SAVE_FILE.exists():
            shutil.copy2(SAVE_FILE, BACKUP_FILE)
        tmp.replace(SAVE_FILE)
        shutil.copy2(SAVE_FILE, RECOVERY_FILE)
        return True
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        try:
            SAVE_FILE.with_suffix(".tmp").unlink(missing_ok=True)
        except OSError:
            pass
        return False
