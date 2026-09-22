from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpaceVisualProfile:
    """Canonical visual dialect layered on top of the shared Awake World DNA."""

    floor_family: str
    surface: str
    material: str
    structure: str
    accent: str
    accent_alt: str
    vegetation: str
    ambient: str
    label: str
    openness: float
    density: float


# MVD-0 contract: materials are intentionally restrained. Technology is expressed
# through composition, state and light behavior rather than neon/cyberpunk styling.
SPACE_VISUAL_PROFILES: dict[str, SpaceVisualProfile] = {
    "quarter": SpaceVisualProfile("plaza", "#DDD9D0", "#C6C0B5", "#8E9492", "#5F6ED1", "#6F9278", "#68886D", "#D9BD78", "#5A6268", .82, .58),
    "central_plaza": SpaceVisualProfile("plaza", "#DDD6C9", "#B8B1A5", "#5E686C", "#78977B", "#B99C68", "#719477", "#D7BD7D", "#5A6268", .88, .46),
    "observatory": SpaceVisualProfile("home", "#D8D0C2", "#88765E", "#56616A", "#6E8F76", "#C09A61", "#6F8E72", "#D7B978", "#596068", .76, .52),
    "grid": SpaceVisualProfile("warm", "#D6D7D5", "#81878D", "#4D555D", "#70818E", "#9C9178", "#70806F", "#C3B37D", "#555D63", .58, .68),
    "twin_core": SpaceVisualProfile("warm", "#C4C8C9", "#6A7074", "#343B40", "#688C99", "#9C846B", "#6D8073", "#B5AE84", "#4E585D", .54, .74),
    "trinity_lab": SpaceVisualProfile("warm", "#E0D6C5", "#A47E58", "#58666B", "#799A79", "#B98A70", "#789675", "#D1B878", "#596268", .68, .62),
    "garage": SpaceVisualProfile("warm", "#C8C1B6", "#806D5B", "#43484C", "#987354", "#728879", "#657864", "#C4A66F", "#55595B", .52, .76),
    "kawaii_garden": SpaceVisualProfile("home", "#E7DAD3", "#B78D84", "#68786F", "#8AA77D", "#C49A9B", "#78986F", "#D9BE87", "#5E6963", .84, .50),
    "pit": SpaceVisualProfile("warm", "#797B7B", "#55504E", "#292D30", "#8D706A", "#887B67", "#687166", "#B69A72", "#C9C6BD", .44, .82),
    "glasshouse": SpaceVisualProfile("home", "#E4E1D6", "#BAC5B8", "#718078", "#7F9B7B", "#B8A07B", "#77967A", "#D7C28B", "#5E6863", .90, .42),
}


def get_space_visual_profile(space_id: str) -> SpaceVisualProfile:
    return SPACE_VISUAL_PROFILES[space_id]
