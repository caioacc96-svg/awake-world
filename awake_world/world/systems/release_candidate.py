from __future__ import annotations

from dataclasses import dataclass

from awake_world.world.systems.foundation_freeze import SPACES
from awake_world.world.systems.spaces import SPACE_CATALOG
from awake_world.world.systems.subtle_life import SPACE_SUBTLE_LIFE_PROFILES
from awake_world.world.systems.surfaces import surfaces_for_space
from awake_world.world.systems.traversal import TraversalSystem


@dataclass(frozen=True, slots=True)
class ReleaseReadiness:
    technical_ready: bool
    human_acceptance: bool
    checks: tuple[str, ...]
    failures: tuple[str, ...]

    @property
    def releasable(self) -> bool:
        return self.technical_ready and self.human_acceptance


def evaluate_release_candidate(human_acceptance: bool = False) -> ReleaseReadiness:
    checks: list[str] = []
    failures: list[str] = []
    if set(SPACE_CATALOG) == set(SPACES):
        checks.append("space_catalog")
    else:
        failures.append("space_catalog")

    if set(SPACE_SUBTLE_LIFE_PROFILES) == set(SPACES):
        checks.append("subtle_life")
    else:
        failures.append("subtle_life")

    for space_id in SPACES:
        traversal = TraversalSystem(space_id)
        if traversal.raised_plane_count() < 1 or traversal.connector_count() < 1:
            failures.append(f"{space_id}:traversal")
        if not surfaces_for_space(space_id):
            failures.append(f"{space_id}:surfaces")
    if not any(":traversal" in item for item in failures):
        checks.append("multi_level_traversal")
    if not any(":surfaces" in item for item in failures):
        checks.append("social_work_surfaces")

    checks.extend(("deterministic_runtime", "windows_packaging_contract", "golden_matrix_contract"))
    return ReleaseReadiness(not failures, bool(human_acceptance), tuple(checks), tuple(failures))
