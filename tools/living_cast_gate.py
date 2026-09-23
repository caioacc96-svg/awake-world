from __future__ import annotations

from pathlib import Path

from awake_world.design.characters import (
    CAIO_MONKS, DIRECTIONS, POSES, direction_from_vector, validate_character_profiles,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures = list(validate_character_profiles())
    expected = {
        (1, 0): "east", (1, -1): "north_east", (0, -1): "north",
        (-1, -1): "north_west", (-1, 0): "west", (-1, 1): "south_west",
        (0, 1): "south", (1, 1): "south_east",
    }
    for vector, direction in expected.items():
        actual = direction_from_vector(*vector)
        if actual != direction:
            failures.append(f"direction:{vector}:{actual}!={direction}")
    if len(DIRECTIONS) != 8:
        failures.append("directions:count")
    if not {"standing", "seated", "working", "listening", "resting", "phone"} <= set(POSES):
        failures.append("poses:contract")
    if CAIO_MONKS.id != "caio_monks" or CAIO_MONKS.accessory != "headphones":
        failures.append("pilot:identity")
    effective_height = CAIO_MONKS.metrics.height_px * CAIO_MONKS.metrics.world_scale
    if not 74 <= effective_height <= 86:
        failures.append(f"pilot:world-scale={effective_height:.1f}px")

    avatar_source = (ROOT / "awake_world/world/avatar.py").read_text(encoding="utf-8")
    for token in ("direction_from_vector", "profile_id", "grid_z", "setZValue", "headphones", "world_scale"):
        if token not in avatar_source:
            failures.append(f"avatar:{token}")
    district = (ROOT / "awake_world/world/district.py").read_text(encoding="utf-8")
    for token in ("MONKS selector console", "selector_screen"):
        if token not in district:
            failures.append(f"observatory:{token}")
    for relative in (
        "tools/render_living_cast.py",
        "docs/AWAKE_WORLD_07_CHARACTER_SPRITE_BIBLE.md",
    ):
        if not (ROOT / relative).exists():
            failures.append(f"missing:{relative}")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != "0.7.0-dev":
        failures.append(f"version:{version}")

    if failures:
        print("AWAKE_LIVING_CAST_LC1_FAILED", *failures, sep="\n")
        return 7
    print("AWAKE_LIVING_CAST_LC1_OK")
    print(f"pilot={CAIO_MONKS.id} directions={len(DIRECTIONS)} poses={len(POSES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
