from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VisualFoundationProfile:
    """MVD-2.1 architectural composition contract.

    These values refine presentation only. They never redefine MVD-1 footprints,
    circulation, collision or landmark hierarchy.
    """

    frame_scale: float
    frame_y_bias: float
    ground_border: float
    joint_spacing: int
    body_inset: float
    plinth_height: float
    cap_height: float
    cap_overhang: float
    facade_bays: int
    glazing_ratio: float
    shadow_offset: float
    shadow_opacity: float
    landscape_layers: int
    accent_inlay: bool = True


SPACE_VISUAL_FOUNDATION_PROFILES: dict[str, VisualFoundationProfile] = {
    "quarter": VisualFoundationProfile(.80, 8.0, .58, 4, .10, .16, .11, .10, 5, .42, .16, .15, 2),
    "central_plaza": VisualFoundationProfile(.78, 18.0, .72, 4, .08, .13, .09, .12, 4, .48, .15, .13, 3),
    "observatory": VisualFoundationProfile(.76, 4.0, .66, 4, .10, .17, .10, .14, 5, .68, .18, .16, 2),
    "grid": VisualFoundationProfile(.78, 7.0, .54, 3, .09, .15, .10, .08, 6, .34, .14, .14, 1),
    "twin_core": VisualFoundationProfile(.77, 5.0, .58, 3, .11, .18, .12, .09, 6, .46, .17, .18, 1),
    "trinity_lab": VisualFoundationProfile(.78, 8.0, .64, 4, .10, .15, .10, .12, 5, .50, .16, .14, 2),
    "garage": VisualFoundationProfile(.79, 8.0, .50, 3, .07, .19, .10, .06, 5, .24, .13, .19, 1),
    "kawaii_garden": VisualFoundationProfile(.77, 15.0, .72, 4, .10, .13, .09, .13, 4, .52, .16, .12, 3),
    "pit": VisualFoundationProfile(.78, 9.0, .48, 3, .08, .20, .11, .07, 5, .22, .12, .22, 1, False),
    "glasshouse": VisualFoundationProfile(.76, 7.0, .74, 4, .08, .12, .08, .14, 6, .78, .18, .11, 3),
}


def get_space_visual_foundation_profile(space_id: str) -> VisualFoundationProfile:
    return SPACE_VISUAL_FOUNDATION_PROFILES[space_id]


def framed_scene_rect(
    scene_rect: tuple[float, float, float, float],
    profile: VisualFoundationProfile,
) -> tuple[float, float, float, float]:
    """Tighten presentation framing without changing gameplay coordinates."""

    x, y, width, height = scene_rect
    framed_width = width * profile.frame_scale
    framed_height = height * profile.frame_scale
    return (
        x + (width - framed_width) / 2.0,
        y + (height - framed_height) / 2.0 + profile.frame_y_bias,
        framed_width,
        framed_height,
    )
