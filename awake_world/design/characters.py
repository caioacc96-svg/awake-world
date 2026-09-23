from __future__ import annotations

from dataclasses import dataclass
import math

LIVING_CAST_VERSION = "0.7.0-dev"

DIRECTIONS: tuple[str, ...] = (
    "east", "north_east", "north", "north_west",
    "west", "south_west", "south", "south_east",
)

POSES: tuple[str, ...] = (
    "standing", "seated", "working", "listening", "resting", "phone",
)


@dataclass(frozen=True)
class SpriteMetrics:
    width_px: float = 82.0
    height_px: float = 126.0
    head_px: float = 39.0
    shoulder_px: float = 47.0
    shadow_px: float = 44.0
    outline_px: float = 1.35


@dataclass(frozen=True)
class CharacterProfile:
    id: str
    display_name: str
    role: str
    skin: str
    hair: str
    jacket: str
    shirt: str
    trousers: str
    shoes: str
    accent: str
    metal: str
    accessory: str
    metrics: SpriteMetrics = SpriteMetrics()


CAIO_MONKS = CharacterProfile(
    id="caio_monks",
    display_name="Caio / MONKS",
    role="Observatory host · selector",
    # Authored stylized pilot identity; not a physical-likeness claim.
    skin="#C99574",
    hair="#24272D",
    jacket="#20242B",
    shirt="#F1EFE7",
    trousers="#30343D",
    shoes="#F3F0E8",
    accent="#B99145",
    metal="#CAD3DC",
    accessory="headphones",
)

CHARACTERS: dict[str, CharacterProfile] = {CAIO_MONKS.id: CAIO_MONKS}


def direction_from_vector(dx: float, dy: float) -> str:
    """Resolve a continuous world-facing vector into eight presentation sectors."""
    if abs(dx) + abs(dy) < 1e-6:
        return "south"
    angle = math.atan2(-dy, dx)
    return DIRECTIONS[round(angle / (math.pi / 4.0)) % 8]


def get_character_profile(profile_id: str = "caio_monks") -> CharacterProfile:
    try:
        return CHARACTERS[profile_id]
    except KeyError as exc:
        raise KeyError(f"Unknown Awake character profile: {profile_id}") from exc


def validate_character_profiles() -> tuple[str, ...]:
    failures: list[str] = []
    if len(DIRECTIONS) != 8 or len(set(DIRECTIONS)) != 8:
        failures.append("directions:not-eight-unique")
    required = {"standing", "seated", "working", "listening", "resting", "phone"}
    if not required <= set(POSES):
        failures.append("poses:missing-required")
    for profile_id, profile in CHARACTERS.items():
        if profile_id != profile.id:
            failures.append(f"{profile_id}:registry-id-mismatch")
        if profile.accessory not in {"headphones", "none"}:
            failures.append(f"{profile_id}:unsupported-accessory")
        for name in ("skin", "hair", "jacket", "shirt", "trousers", "shoes", "accent", "metal"):
            value = str(getattr(profile, name))
            if len(value) != 7 or not value.startswith("#"):
                failures.append(f"{profile_id}:{name}:invalid-color")
        m = profile.metrics
        if not 72 <= m.width_px <= 96:
            failures.append(f"{profile_id}:width")
        if not 112 <= m.height_px <= 136:
            failures.append(f"{profile_id}:height")
        if not 34 <= m.head_px <= 44:
            failures.append(f"{profile_id}:head")
        if m.outline_px > 1.6:
            failures.append(f"{profile_id}:outline")
    return tuple(failures)
