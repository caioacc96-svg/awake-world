from __future__ import annotations

from dataclasses import dataclass

from awake_world.design.spatial_depth import StairFlight, get_space_spatial_depth_profile


@dataclass(frozen=True, slots=True)
class TraversalSample:
    elevation: float
    source: str
    connector: bool = False


class TraversalSystem:
    """Authored 2.5D traversal over MVD-2.2 planes; no general-purpose 3D physics."""

    MAX_DIRECT_STEP = .085

    def __init__(self, space_id: str) -> None:
        self.space_id = space_id
        self.profile = get_space_spatial_depth_profile(space_id)

    @staticmethod
    def _inside(x: float, y: float, rx: float, ry: float, rw: float, rd: float, pad: float = 0.0) -> bool:
        return rx - pad <= x <= rx + rw + pad and ry - pad <= y <= ry + rd + pad

    @staticmethod
    def _stair_sample(stair: StairFlight, x: float, y: float) -> TraversalSample | None:
        run = max(.001, stair.run)
        if stair.axis == "y":
            offset = (y - stair.y) * stair.direction
            lateral = x - stair.x
            if not (-.08 <= lateral <= stair.width + .08 and -.05 <= offset <= run + .05):
                return None
        else:
            offset = (x - stair.x) * stair.direction
            lateral = y - stair.y
            if not (-.08 <= lateral <= stair.width + .08 and -.05 <= offset <= run + .05):
                return None
        q = min(1.0, max(0.0, offset / run))
        return TraversalSample(round(stair.rise * (1.0 - q), 4), "stair", True)

    def sample(self, x: float, y: float) -> TraversalSample:
        for stair in self.profile.stairs:
            value = self._stair_sample(stair, x, y)
            if value is not None:
                return value

        elevation = 0.0
        source = "grade"
        for plane in self.profile.planes:
            if self._inside(x, y, plane.x, plane.y, plane.w, plane.d):
                if plane.h >= elevation:
                    elevation = plane.h
                    source = plane.kind
        return TraversalSample(round(elevation, 4), source, False)

    def elevation_at(self, x: float, y: float) -> float:
        return self.sample(x, y).elevation

    def can_transition(
        self,
        current_x: float,
        current_y: float,
        current_z: float,
        target_x: float,
        target_y: float,
    ) -> bool:
        current = self.sample(current_x, current_y)
        target = self.sample(target_x, target_y)
        reference_z = current_z if abs(current_z - current.elevation) <= .16 else current.elevation
        delta = abs(target.elevation - reference_z)
        if delta <= self.MAX_DIRECT_STEP:
            return True
        if current.connector or target.connector:
            return delta <= max(.12, max((s.rise / max(1, s.steps) for s in self.profile.stairs), default=.08) * 1.75)
        return False

    def connector_count(self) -> int:
        return len(self.profile.stairs)

    def raised_plane_count(self) -> int:
        return len(self.profile.planes)
