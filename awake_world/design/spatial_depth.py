from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RaisedPlane:
    x: float
    y: float
    w: float
    d: float
    h: float
    kind: str = "terrace"


@dataclass(frozen=True, slots=True)
class StairFlight:
    x: float
    y: float
    width: float
    run: float
    rise: float
    steps: int
    axis: str = "y"
    direction: int = 1


@dataclass(frozen=True, slots=True)
class PierLine:
    x: float
    y: float
    count: int
    dx: float
    dy: float
    w: float
    d: float
    h: float


@dataclass(frozen=True, slots=True)
class SpatialDepthProfile:
    """MVD-2.2 visual depth contract.

    Terrain depth is architectural/presentation-only in this phase. It must not
    redefine the MVD-1 navigation plane, collision footprint or circulation
    contract.
    """

    upper_setback: float
    split_ratio: float
    floor_reveal: float
    planes: tuple[RaisedPlane, ...] = ()
    stairs: tuple[StairFlight, ...] = ()
    piers: tuple[PierLine, ...] = ()


SPACE_SPATIAL_DEPTH_PROFILES: dict[str, SpatialDepthProfile] = {
    "quarter": SpatialDepthProfile(
        .10, .58, .055,
        (
            RaisedPlane(9.70, 6.35, 4.55, 1.15, .22, "civic_dais"),
            RaisedPlane(2.70, 11.75, 5.85, .70, .14, "garden_edge"),
        ),
        (
            StairFlight(11.05, 7.35, 1.85, .82, .22, 4, "y", -1),
            StairFlight(5.05, 12.45, 1.45, .56, .14, 3, "y", -1),
        ),
        (
            PierLine(9.95, 6.58, 4, 1.34, 0.0, .10, .10, 1.15),
        ),
    ),
    "central_plaza": SpatialDepthProfile(
        .08, .54, .050,
        (
            RaisedPlane(6.75, 4.75, 4.50, 3.65, .24, "canopy_stage"),
            RaisedPlane(2.25, 8.15, 3.70, 1.00, .14, "seat_terrace"),
        ),
        (
            StairFlight(7.55, 8.40, 2.85, .88, .24, 4, "y", -1),
            StairFlight(3.15, 9.15, 1.85, .58, .14, 3, "y", -1),
        ),
        (
            PierLine(7.05, 5.05, 3, 1.95, 0.0, .12, .12, 2.20),
        ),
    ),
    "observatory": SpatialDepthProfile(
        .12, .60, .060,
        (
            RaisedPlane(5.45, 6.55, 6.15, 2.05, .30, "view_terrace"),
            RaisedPlane(6.35, 2.20, 4.30, 1.25, .18, "instrument_deck"),
        ),
        (
            StairFlight(7.25, 8.60, 2.55, .92, .30, 5, "y", -1),
            StairFlight(7.35, 3.45, 2.30, .72, .18, 3, "y", -1),
        ),
        (
            PierLine(5.75, 6.80, 4, 1.75, 0.0, .10, .10, 1.35),
        ),
    ),
    "grid": SpatialDepthProfile(
        .08, .56, .045,
        (
            RaisedPlane(4.85, 4.65, 5.35, 2.65, .22, "operations_bridge"),
            RaisedPlane(10.15, 7.15, 3.70, 1.05, .14, "ops_step"),
        ),
        (
            StairFlight(6.60, 7.30, 1.80, .76, .22, 4, "y", -1),
            StairFlight(11.15, 8.20, 1.55, .56, .14, 3, "y", -1),
        ),
        (
            PierLine(5.10, 5.00, 4, 1.45, 0.0, .10, .10, 1.55),
        ),
    ),
    "twin_core": SpatialDepthProfile(
        .14, .62, .065,
        (
            RaisedPlane(5.95, 3.25, 6.10, 2.55, .26, "core_bridge"),
            RaisedPlane(6.65, 7.70, 4.70, 1.15, .16, "dev_terrace"),
        ),
        (
            StairFlight(8.00, 5.80, 2.00, .84, .26, 4, "y", -1),
            StairFlight(8.10, 8.85, 1.80, .62, .16, 3, "y", -1),
        ),
        (
            PierLine(6.20, 3.55, 4, 1.78, 0.0, .12, .12, 1.75),
        ),
    ),
    "trinity_lab": SpatialDepthProfile(
        .10, .57, .055,
        (
            RaisedPlane(5.95, 7.30, 6.10, 2.80, .24, "research_terrace"),
            RaisedPlane(6.55, 2.05, 4.90, 1.10, .16, "lab_bridge"),
        ),
        (
            StairFlight(7.65, 10.10, 2.35, .82, .24, 4, "y", -1),
            StairFlight(7.85, 3.15, 2.00, .60, .16, 3, "y", -1),
        ),
        (
            PierLine(6.35, 7.65, 4, 1.70, 0.0, .10, .10, 1.45),
        ),
    ),
    "garage": SpatialDepthProfile(
        .06, .52, .045,
        (
            RaisedPlane(4.95, 5.90, 6.10, 2.55, .18, "service_bay"),
            RaisedPlane(1.25, 8.30, 3.65, 1.25, .12, "loading_dock"),
        ),
        (
            StairFlight(7.00, 8.45, 2.05, .70, .18, 3, "y", -1),
            StairFlight(2.35, 9.55, 1.55, .48, .12, 3, "y", -1),
        ),
        (
            PierLine(5.20, 6.15, 4, 1.75, 0.0, .12, .12, 1.35),
        ),
    ),
    "kawaii_garden": SpatialDepthProfile(
        .10, .56, .050,
        (
            RaisedPlane(5.85, 3.75, 5.30, 3.65, .22, "garden_pavilion"),
            RaisedPlane(1.65, 9.45, 3.25, 1.15, .12, "garden_step"),
        ),
        (
            StairFlight(7.35, 7.40, 2.30, .78, .22, 4, "y", -1),
            StairFlight(2.45, 10.60, 1.65, .52, .12, 3, "y", -1),
        ),
        (
            PierLine(6.15, 4.05, 4, 1.55, 0.0, .09, .09, 1.45),
        ),
    ),
    "pit": SpatialDepthProfile(
        .05, .50, .040,
        (
            RaisedPlane(4.55, 3.55, 6.90, 4.45, .10, "sunken_ring"),
            RaisedPlane(5.30, 4.35, 5.40, 2.95, .18, "inner_ring"),
            RaisedPlane(6.05, 5.10, 3.90, 1.55, .26, "social_core"),
        ),
        (
            StairFlight(6.65, 7.30, 2.70, .70, .26, 5, "y", -1),
        ),
        (),
    ),
    "glasshouse": SpatialDepthProfile(
        .12, .60, .055,
        (
            RaisedPlane(5.35, 3.55, 6.25, 2.35, .20, "greenhouse_deck"),
            RaisedPlane(1.35, 7.85, 4.20, 1.10, .12, "plant_terrace"),
        ),
        (
            StairFlight(7.30, 5.90, 2.35, .76, .20, 4, "y", -1),
            StairFlight(2.55, 8.95, 1.80, .52, .12, 3, "y", -1),
        ),
        (
            PierLine(5.65, 3.85, 4, 1.83, 0.0, .09, .09, 1.55),
        ),
    ),
}


def get_space_spatial_depth_profile(space_id: str) -> SpatialDepthProfile:
    return SPACE_SPATIAL_DEPTH_PROFILES[space_id]
