from __future__ import annotations

from dataclasses import dataclass


HUMAN_SCALE_UNITS = 2.35


@dataclass(frozen=True, slots=True)
class MassingVolume:
    """A physical volume in tile-space. Role describes hierarchy, never palette."""

    x: float
    y: float
    w: float
    d: float
    h: float
    role: str = "support"


@dataclass(frozen=True, slots=True)
class CirculationBand:
    """Negative-space corridor or civic surface that remains intentionally open."""

    x: float
    y: float
    w: float
    d: float


@dataclass(frozen=True, slots=True)
class SpaceMassingProfile:
    """MVD-1 spatial contract for silhouette, scale, hierarchy and circulation."""

    width_tiles: int
    depth_tiles: int
    spawn: tuple[float, float]
    scene_rect: tuple[float, float, float, float]
    axis: str
    landmark: str
    circulation: tuple[CirculationBand, ...]
    volumes: tuple[MassingVolume, ...]
    vegetation_points: tuple[tuple[float, float, float], ...] = ()

    @property
    def landmark_volumes(self) -> tuple[MassingVolume, ...]:
        return tuple(volume for volume in self.volumes if volume.role == "landmark")


SPACE_MASSING_PROFILES: dict[str, SpaceMassingProfile] = {
    "quarter": SpaceMassingProfile(
        24, 18, (11.8, 15.5), (-1540.0, -760.0, 3080.0, 2140.0), "cross", "civic_spine",
        (
            CirculationBand(1.0, 7.35, 22.0, 2.35),
            CirculationBand(10.45, .75, 2.75, 16.5),
            CirculationBand(2.2, 12.0, 7.0, 1.35),
            CirculationBand(14.8, 5.0, 7.2, 1.35),
        ),
        (
            MassingVolume(1.2, .75, 4.7, 1.55, 2.9, "primary"),
            MassingVolume(6.5, .55, 3.8, 1.45, 3.35, "primary"),
            MassingVolume(10.8, .35, 4.25, 1.35, 3.05, "landmark"),
            MassingVolume(15.55, .75, 5.75, 1.65, 2.75, "primary"),
            MassingVolume(20.45, 4.2, 1.7, 2.0, 2.6, "primary"),
            MassingVolume(18.15, 13.8, 3.7, 1.7, 1.7, "support"),
            MassingVolume(12.55, 13.35, 4.1, 1.25, 1.35, "support"),
            MassingVolume(3.45, 12.45, 4.6, 1.35, 2.05, "primary"),
        ),
        ((2.0, 10.7, 1.05), (4.2, 10.0, .92), (7.5, 6.25, 1.08), (8.7, 11.9, .95), (16.8, 10.4, 1.12), (20.6, 10.9, .98)),
    ),
    "central_plaza": SpaceMassingProfile(
        18, 14, (8.8, 11.8), (-1180.0, -470.0, 2360.0, 1580.0), "cross", "civic_canopy",
        (
            CirculationBand(7.25, .6, 3.5, 12.5),
            CirculationBand(.9, 5.5, 16.2, 2.5),
            CirculationBand(3.0, 2.0, 3.8, 2.9),
        ),
        (
            MassingVolume(.7, .65, 4.0, .55, .72, "support"),
            MassingVolume(13.2, .65, 4.0, .55, .72, "support"),
            MassingVolume(2.2, 2.0, 3.4, 2.3, .55, "support"),
            MassingVolume(12.5, 2.0, 3.1, 1.65, 1.15, "primary"),
            MassingVolume(12.0, 8.5, 3.2, 1.75, 1.0, "primary"),
            MassingVolume(7.45, 5.2, .22, 2.8, 2.65, "landmark"),
            MassingVolume(10.35, 5.2, .22, 2.8, 2.65, "landmark"),
            MassingVolume(7.45, 5.2, 3.12, .22, .18, "landmark"),
        ),
        ((1.7, 3.0, 1.15), (2.8, 4.2, .95), (4.2, 3.1, 1.05), (15.8, 8.0, 1.0)),
    ),
    "observatory": SpaceMassingProfile(
        17, 12, (8.25, 10.05), (-1120.0, -500.0, 2240.0, 1510.0), "long_view", "horizon_frame",
        (
            CirculationBand(2.1, 7.45, 12.8, 2.0),
            CirculationBand(7.25, 2.0, 2.5, 7.8),
        ),
        (
            MassingVolume(.7, .55, 5.1, .55, 2.85, "primary"),
            MassingVolume(11.0, .55, 5.25, .55, 2.85, "primary"),
            MassingVolume(.7, .55, .55, 7.0, 2.5, "support"),
            MassingVolume(15.7, .55, .55, 7.0, 2.5, "support"),
            MassingVolume(5.85, 2.6, 5.4, 1.2, .78, "support"),
            MassingVolume(6.45, .65, .24, 2.4, 3.45, "landmark"),
            MassingVolume(10.25, .65, .24, 2.4, 3.45, "landmark"),
            MassingVolume(6.45, .65, 4.04, .24, .20, "landmark"),
        ),
        ((2.0, 9.0, 1.15), (14.5, 8.8, 1.1), (12.3, 6.1, .95)),
    ),
    "grid": SpaceMassingProfile(
        15, 13, (7.2, 11.0), (-1030.0, -480.0, 2060.0, 1510.0), "parallel", "operations_bridge",
        (
            CirculationBand(3.2, 1.2, 1.7, 10.3),
            CirculationBand(8.3, 1.2, 1.7, 10.3),
            CirculationBand(3.2, 5.5, 8.3, 1.7),
        ),
        (
            MassingVolume(.75, .7, 1.75, 9.0, 2.35, "primary"),
            MassingVolume(5.35, .7, 2.2, 3.3, 1.45, "support"),
            MassingVolume(10.8, .7, 3.35, 3.0, 2.55, "primary"),
            MassingVolume(10.8, 7.4, 3.35, 2.8, 2.55, "primary"),
            MassingVolume(5.2, 7.5, 2.6, 2.0, 1.25, "support"),
            MassingVolume(4.4, 5.0, 4.7, .34, 3.15, "landmark"),
        ),
        ((13.0, 10.6, .85),),
    ),
    "twin_core": SpaceMassingProfile(
        18, 12, (8.8, 10.0), (-1160.0, -490.0, 2320.0, 1500.0), "dual", "twin_monoliths",
        (
            CirculationBand(7.45, 1.0, 3.0, 9.6),
            CirculationBand(2.0, 6.0, 14.0, 1.5),
        ),
        (
            MassingVolume(1.0, .8, 4.5, 2.4, 3.15, "landmark"),
            MassingVolume(12.5, .8, 4.5, 2.4, 3.15, "landmark"),
            MassingVolume(1.3, 7.7, 4.2, 1.75, 1.55, "primary"),
            MassingVolume(12.5, 7.7, 4.2, 1.75, 1.55, "primary"),
            MassingVolume(6.3, 3.7, 5.4, 1.6, .95, "support"),
            MassingVolume(6.3, 8.2, 5.4, .7, .65, "support"),
        ),
        ((8.8, 2.4, .85),),
    ),
    "trinity_lab": SpaceMassingProfile(
        18, 13, (8.7, 11.0), (-1180.0, -500.0, 2360.0, 1580.0), "triangle", "research_terrace",
        (
            CirculationBand(7.25, 1.2, 3.4, 10.0),
            CirculationBand(2.1, 6.0, 13.8, 1.7),
        ),
        (
            MassingVolume(.8, .65, 4.7, 1.0, 2.55, "primary"),
            MassingVolume(12.5, .65, 4.7, 1.0, 2.55, "primary"),
            MassingVolume(1.2, 2.8, 3.7, 2.0, 1.35, "support"),
            MassingVolume(13.0, 2.8, 3.7, 2.0, 1.35, "support"),
            MassingVolume(6.2, 7.9, 5.6, 1.9, .95, "primary"),
            MassingVolume(6.6, .9, 4.8, .75, 2.1, "landmark"),
            MassingVolume(7.2, .9, 3.6, .75, 2.95, "landmark"),
        ),
        ((2.0, 10.1, 1.0), (15.9, 10.0, 1.0), (11.8, 5.1, .9)),
    ),
    "garage": SpaceMassingProfile(
        16, 12, (7.7, 10.1), (-1080.0, -510.0, 2160.0, 1510.0), "bay", "service_door",
        (
            CirculationBand(5.4, .8, 5.0, 10.4),
            CirculationBand(1.2, 6.8, 13.5, 1.8),
        ),
        (
            MassingVolume(.7, .65, 4.1, 8.6, 2.7, "primary"),
            MassingVolume(11.2, .65, 4.0, 8.6, 2.7, "primary"),
            MassingVolume(5.1, .6, 5.8, .55, 3.65, "landmark"),
            MassingVolume(1.4, 8.6, 3.2, 1.55, 1.15, "support"),
            MassingVolume(11.5, 8.6, 2.9, 1.55, 1.15, "support"),
        ),
        ((13.8, 10.2, .82),),
    ),
    "kawaii_garden": SpaceMassingProfile(
        17, 13, (8.15, 11.0), (-1120.0, -500.0, 2240.0, 1580.0), "meander", "garden_pavilion",
        (
            CirculationBand(1.8, 7.3, 13.5, 2.2),
            CirculationBand(6.6, 2.1, 3.1, 8.7),
        ),
        (
            MassingVolume(.8, .7, 4.4, 1.0, 1.75, "primary"),
            MassingVolume(11.8, .7, 4.4, 1.0, 1.75, "primary"),
            MassingVolume(2.0, 3.0, 3.6, 2.0, .58, "support"),
            MassingVolume(11.1, 3.2, 3.8, 2.0, .58, "support"),
            MassingVolume(6.25, 4.2, .22, 2.8, 2.55, "landmark"),
            MassingVolume(9.65, 4.2, .22, 2.8, 2.55, "landmark"),
            MassingVolume(6.25, 4.2, 3.62, .22, .18, "landmark"),
        ),
        ((1.6, 10.2, 1.2), (3.0, 6.2, 1.0), (13.9, 6.1, 1.05), (15.1, 10.0, 1.15), (8.0, 3.2, .95)),
    ),
    "pit": SpaceMassingProfile(
        16, 12, (7.65, 10.0), (-1080.0, -500.0, 2160.0, 1510.0), "compressed_ring", "sunken_social_core",
        (
            CirculationBand(5.0, 3.6, 6.0, 5.0),
            CirculationBand(1.0, 8.8, 14.0, 1.45),
        ),
        (
            MassingVolume(.65, .6, 14.7, .8, 3.0, "primary"),
            MassingVolume(.65, 1.0, 2.0, 7.2, 2.35, "primary"),
            MassingVolume(13.35, 1.0, 2.0, 7.2, 2.35, "primary"),
            MassingVolume(3.2, 2.0, 3.0, 1.2, 1.1, "support"),
            MassingVolume(9.8, 2.0, 3.0, 1.2, 1.1, "support"),
            MassingVolume(4.8, 4.0, 6.4, .55, .55, "landmark"),
            MassingVolume(5.5, 4.8, 5.0, .55, .38, "landmark"),
            MassingVolume(6.2, 5.6, 3.6, 1.8, .22, "landmark"),
        ),
        (),
    ),
    "glasshouse": SpaceMassingProfile(
        17, 12, (8.1, 10.0), (-1120.0, -500.0, 2240.0, 1510.0), "porous", "greenhouse_ribs",
        (
            CirculationBand(6.7, 1.1, 3.6, 9.4),
            CirculationBand(1.3, 7.1, 14.4, 1.7),
        ),
        (
            MassingVolume(.7, .65, 15.6, .3, 2.45, "primary"),
            MassingVolume(.7, .65, .3, 7.7, 2.45, "primary"),
            MassingVolume(16.0, .65, .3, 7.7, 2.45, "primary"),
            MassingVolume(1.5, 2.2, 3.4, 1.5, .55, "support"),
            MassingVolume(12.1, 2.2, 3.4, 1.5, .55, "support"),
            MassingVolume(6.0, 4.0, 5.0, 1.25, .48, "support"),
            MassingVolume(5.8, .8, .2, 6.5, 3.05, "landmark"),
            MassingVolume(11.0, .8, .2, 6.5, 3.05, "landmark"),
            MassingVolume(5.8, .8, 5.4, .2, .18, "landmark"),
        ),
        ((2.0, 9.0, 1.15), (4.1, 6.0, .95), (13.2, 6.1, 1.0), (15.0, 9.0, 1.15), (8.5, 2.8, .9)),
    ),
}


def get_space_massing_profile(space_id: str) -> SpaceMassingProfile:
    return SPACE_MASSING_PROFILES[space_id]
