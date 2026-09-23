from __future__ import annotations

from dataclasses import dataclass


SPACES = (
    "quarter", "central_plaza", "observatory", "grid", "twin_core",
    "trinity_lab", "garage", "kawaii_garden", "pit", "glasshouse",
)


@dataclass(frozen=True, slots=True)
class GoldenMatrixEntry:
    key: str
    space_id: str
    minute: int
    weather: str
    frame: str


def build_foundation_matrix() -> tuple[GoldenMatrixEntry, ...]:
    entries: list[GoldenMatrixEntry] = []
    for space_id in SPACES:
        entries.extend((
            GoldenMatrixEntry(f"mvd5_{space_id}_day_clear_nav", space_id, 11 * 60, "clear", "navigation"),
            GoldenMatrixEntry(f"mvd5_{space_id}_night_rain_idle", space_id, 22 * 60, "rain", "idle_life"),
            GoldenMatrixEntry(f"mvd5_{space_id}_dusk_interaction", space_id, 18 * 60, "clear", "interaction"),
        ))
    return tuple(entries)


FOUNDATION_GOLDEN_MATRIX = build_foundation_matrix()


def validate_foundation_matrix() -> tuple[str, ...]:
    failures: list[str] = []
    for space_id in SPACES:
        rows = [row for row in FOUNDATION_GOLDEN_MATRIX if row.space_id == space_id]
        frames = {row.frame for row in rows}
        weather = {row.weather for row in rows}
        if frames != {"navigation", "idle_life", "interaction"}:
            failures.append(f"{space_id}:frames")
        if "clear" not in weather or "rain" not in weather:
            failures.append(f"{space_id}:weather")
        if not any(row.minute >= 20 * 60 for row in rows):
            failures.append(f"{space_id}:night")
    return tuple(failures)
