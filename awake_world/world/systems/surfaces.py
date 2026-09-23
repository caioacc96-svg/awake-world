from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SurfaceRole(StrEnum):
    WORK = "work"
    SOCIAL = "social"
    MEDIA = "media"
    TRANSIT = "transit"


@dataclass(frozen=True, slots=True)
class SurfaceDefinition:
    id: str
    space_id: str
    kind: str
    role: SurfaceRole
    x: float
    y: float
    z: float = 0.0
    capacity: int = 1
    label: str = ""
    action: str = "surface"
    priority: float = 0.0


SURFACES: tuple[SurfaceDefinition, ...] = (
    SurfaceDefinition("quarter.wayfinding", "quarter", "project_board", SurfaceRole.TRANSIT, 11.8, 7.8, label="Quarter network map", priority=.8),
    SurfaceDefinition("quarter.bench", "quarter", "sofa", SurfaceRole.SOCIAL, 10.6, 10.1, capacity=3, label="Civic bench", priority=.3),
    SurfaceDefinition("plaza.cafe", "central_plaza", "desk", SurfaceRole.WORK, 3.8, 5.8, capacity=2, label="Commons counter", priority=.6),
    SurfaceDefinition("plaza.table", "central_plaza", "meeting_table", SurfaceRole.SOCIAL, 8.8, 8.7, z=.14, capacity=4, label="Garden table", priority=.7),
    SurfaceDefinition("observatory.desk", "observatory", "desk", SurfaceRole.WORK, 7.7, 7.3, z=.30, capacity=1, label="Main desk", priority=1.0),
    SurfaceDefinition("observatory.projects", "observatory", "project_board", SurfaceRole.WORK, 8.6, 3.1, z=.18, capacity=2, label="Project wall", priority=.9),
    SurfaceDefinition("observatory.meeting", "observatory", "meeting_table", SurfaceRole.SOCIAL, 9.4, 7.5, z=.30, capacity=4, label="Review table", priority=.7),
    SurfaceDefinition("grid.ops", "grid", "desk", SurfaceRole.WORK, 7.0, 5.8, z=.22, capacity=1, label="Operations console", priority=1.0),
    SurfaceDefinition("grid.board", "grid", "project_board", SurfaceRole.WORK, 9.0, 7.7, z=.14, capacity=2, label="Systems board", priority=.8),
    SurfaceDefinition("twin.left", "twin_core", "workstation", SurfaceRole.WORK, 7.0, 4.7, z=.26, capacity=1, label="Dev station A", priority=1.0),
    SurfaceDefinition("twin.right", "twin_core", "workstation", SurfaceRole.WORK, 10.1, 4.7, z=.26, capacity=1, label="Dev station B", priority=1.0),
    SurfaceDefinition("twin.lab", "twin_core", "lab_workbench", SurfaceRole.WORK, 8.7, 8.1, z=.16, capacity=2, label="Hardware bench", priority=.8),
    SurfaceDefinition("trinity.table", "trinity_lab", "meeting_table", SurfaceRole.WORK, 8.4, 8.7, z=.24, capacity=3, label="Research table", priority=.9),
    SurfaceDefinition("trinity.wall", "trinity_lab", "project_board", SurfaceRole.WORK, 8.7, 2.8, z=.16, capacity=2, label="Experiment wall", priority=.8),
    SurfaceDefinition("garage.bench", "garage", "lab_workbench", SurfaceRole.WORK, 7.8, 7.0, z=.18, capacity=2, label="Prototype bench", priority=1.0),
    SurfaceDefinition("garage.files", "garage", "files", SurfaceRole.WORK, 3.4, 9.0, z=.12, capacity=1, label="Parts archive", priority=.6),
    SurfaceDefinition("garden.bench", "kawaii_garden", "sofa", SurfaceRole.SOCIAL, 8.0, 7.0, z=.22, capacity=3, label="Garden bench", priority=.7),
    SurfaceDefinition("garden.media", "kawaii_garden", "media_surface", SurfaceRole.MEDIA, 8.5, 5.2, z=.22, capacity=2, label="Garden display", priority=.6),
    SurfaceDefinition("pit.sofa", "pit", "sofa", SurfaceRole.SOCIAL, 8.0, 6.0, z=.26, capacity=4, label="Pit sofa", priority=.8),
    SurfaceDefinition("pit.arcade", "pit", "arcade", SurfaceRole.SOCIAL, 9.6, 5.3, z=.18, capacity=2, label="Arcade station", priority=.9),
    SurfaceDefinition("pit.display", "pit", "display", SurfaceRole.MEDIA, 6.5, 5.2, z=.18, capacity=4, label="Shared display", priority=.7),
    SurfaceDefinition("glasshouse.desk", "glasshouse", "desk", SurfaceRole.WORK, 8.3, 4.8, z=.20, capacity=1, label="Climate desk", priority=.8),
    SurfaceDefinition("glasshouse.bench", "glasshouse", "sofa", SurfaceRole.SOCIAL, 3.5, 8.4, z=.12, capacity=2, label="Plant bench", priority=.5),
)


def surfaces_for_space(space_id: str) -> tuple[SurfaceDefinition, ...]:
    return tuple(surface for surface in SURFACES if surface.space_id == space_id)


class SurfaceOccupancySystem:
    """Persistence-friendly occupancy contract for future network replication."""

    def __init__(self, state) -> None:
        self.state = state

    def _store(self, space_id: str) -> dict[str, list[str]]:
        raw = self.state.space_states.setdefault(space_id, {})
        value = raw.setdefault("surface_occupancy", {})
        if not isinstance(value, dict):
            value = {}
            raw["surface_occupancy"] = value
        return value

    def occupy(self, surface: SurfaceDefinition, member_id: str) -> bool:
        store = self._store(surface.space_id)
        occupants = [str(v) for v in store.get(surface.id, [])]
        if member_id in occupants:
            return True
        if len(occupants) >= surface.capacity:
            return False
        occupants.append(member_id)
        store[surface.id] = occupants
        return True

    def release(self, surface: SurfaceDefinition, member_id: str) -> None:
        store = self._store(surface.space_id)
        occupants = [str(v) for v in store.get(surface.id, []) if str(v) != member_id]
        if occupants:
            store[surface.id] = occupants
        else:
            store.pop(surface.id, None)

    def snapshot(self, space_id: str) -> dict[str, tuple[str, ...]]:
        return {key: tuple(str(v) for v in values) for key, values in self._store(space_id).items()}
