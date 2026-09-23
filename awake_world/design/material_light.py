from __future__ import annotations

from dataclasses import dataclass

from awake_world.design.world_visuals import get_space_visual_profile


RGB = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class MaterialLightProfile:
    """MVD-2 local dialect constrained by the shared Awake World material language."""

    primary_family: str
    secondary_family: str
    landmark_family: str
    glass_mode: str
    glass_opacity: float
    temperature_bias: float
    contrast: float
    weather_response: float


@dataclass(frozen=True, slots=True)
class ResolvedSpaceAppearance:
    """Renderer-ready colors after phase and weather response are applied."""

    floor_a: str
    floor_b: str
    floor_edge: str
    surface: str
    material: str
    structure: str
    circulation: str
    glass: str
    vegetation: str
    ambient: str
    accent: str
    label: str
    glass_opacity: float
    phase_wash: str
    phase_wash_alpha: int
    weather_wash: str
    weather_wash_alpha: int


SPACE_MATERIAL_LIGHT_PROFILES: dict[str, MaterialLightProfile] = {
    "quarter": MaterialLightProfile("limestone", "brushed_metal", "stone_glass", "framed", .88, .04, .54, .72),
    "central_plaza": MaterialLightProfile("civic_stone", "timber", "canopy_glass", "framed", .84, .12, .46, .78),
    "observatory": MaterialLightProfile("warm_stone", "oak", "low_iron_glass", "full", .78, .10, .42, .68),
    "grid": MaterialLightProfile("mineral_panel", "anodized_metal", "technical_glass", "recessed", .90, -.10, .62, .64),
    "twin_core": MaterialLightProfile("dark_composite", "graphite_metal", "smoked_glass", "framed", .86, -.16, .72, .60),
    "trinity_lab": MaterialLightProfile("warm_plaster", "oak", "research_glass", "framed", .84, .16, .50, .70),
    "garage": MaterialLightProfile("sealed_concrete", "weathered_wood", "wired_glass", "recessed", .92, .08, .68, .82),
    "kawaii_garden": MaterialLightProfile("soft_plaster", "light_wood", "garden_glass", "framed", .82, .20, .38, .86),
    "pit": MaterialLightProfile("charcoal_concrete", "dark_timber", "smoked_glass", "recessed", .93, .06, .78, .58),
    "glasshouse": MaterialLightProfile("pale_stone", "light_metal", "low_iron_glass", "full", .72, .14, .34, .94),
}


PHASE_EXPOSURE = {
    "dawn": .94,
    "day": 1.0,
    "dusk": .84,
    "night": .70,
}
WEATHER_EXPOSURE = {
    "clear": 1.0,
    "cloudy": .93,
    "rain": .90,
}
PHASE_TINT: dict[str, RGB] = {
    "dawn": (244, 206, 170),
    "day": (238, 239, 233),
    "dusk": (222, 156, 116),
    "night": (91, 108, 137),
}
WEATHER_TINT: dict[str, RGB] = {
    "clear": (235, 236, 229),
    "cloudy": (145, 157, 166),
    "rain": (104, 123, 143),
}


def _rgb(value: str) -> RGB:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]


def _hex(value: RGB) -> str:
    return "#" + "".join(f"{max(0, min(channel, 255)):02X}" for channel in value)


def _mix(a: RGB, b: RGB, amount: float) -> RGB:
    t = max(0.0, min(float(amount), 1.0))
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))  # type: ignore[return-value]


def _scale(value: RGB, factor: float) -> RGB:
    return tuple(round(channel * factor) for channel in value)  # type: ignore[return-value]


def _contrast_about_mid(value: RGB, factor: float) -> RGB:
    """Preserve authored depth after low-light/weather tinting without adding glow."""
    factor = max(1.0, min(float(factor), 1.55))
    return tuple(
        round(128 + (channel - 128) * factor)
        for channel in value
    )  # type: ignore[return-value]


def _respond(
    value: str,
    phase: str,
    weather: str,
    profile: MaterialLightProfile,
    reflectance: float = 1.0,
) -> str:
    phase = phase if phase in PHASE_EXPOSURE else "day"
    weather = weather if weather in WEATHER_EXPOSURE else "clear"
    exposure = PHASE_EXPOSURE[phase] * WEATHER_EXPOSURE[weather] * reflectance
    color = _scale(_rgb(value), exposure)

    phase_amount = {
        "day": .018,
        "dawn": .075,
        "dusk": .115,
        "night": .145,
    }[phase]
    if profile.temperature_bias > 0 and phase in {"dawn", "dusk"}:
        phase_amount += profile.temperature_bias * .04
    elif profile.temperature_bias < 0 and phase == "night":
        phase_amount += abs(profile.temperature_bias) * .05
    color = _mix(color, PHASE_TINT[phase], phase_amount)

    weather_amount = {
        "clear": 0.0,
        "cloudy": .045,
        "rain": .085,
    }[weather] * profile.weather_response
    color = _mix(color, WEATHER_TINT[weather], weather_amount)

    # Night + rain used to collapse distinct material families into one grey-blue
    # band. Restore local material separation while keeping the overall exposure
    # restrained; higher-contrast dialects retain slightly more edge definition.
    if phase == "night":
        boost = 1.16 + max(0.0, profile.contrast - .34) * .48
        if weather == "rain":
            boost += .10
        color = _contrast_about_mid(color, boost)

    mid = (128, 128, 128)
    contrast_amount = max(-.2, min(.2, profile.contrast - .5)) * .22
    if contrast_amount >= 0:
        color = _mix(color, _scale(color, 1.08), contrast_amount)
    else:
        color = _mix(color, mid, abs(contrast_amount))
    return _hex(color)


def _mixed_hex(a: str, b: str, amount: float) -> str:
    return _hex(_mix(_rgb(a), _rgb(b), amount))


def get_space_material_light_profile(space_id: str) -> MaterialLightProfile:
    return SPACE_MATERIAL_LIGHT_PROFILES[space_id]


def resolve_space_appearance(
    space_id: str,
    phase: str = "day",
    weather: str = "clear",
) -> ResolvedSpaceAppearance:
    visual = get_space_visual_profile(space_id)
    profile = get_space_material_light_profile(space_id)
    phase = phase if phase in PHASE_EXPOSURE else "day"
    weather = weather if weather in WEATHER_EXPOSURE else "clear"

    floor_seed = _mixed_hex(visual.surface, visual.material, .12)
    floor_alt_seed = _mixed_hex(visual.surface, visual.material, .22)
    circulation_seed = _mixed_hex(visual.surface, visual.structure, .24)
    glass_seed = _mixed_hex(visual.surface, "#BFD1D2", .58)

    phase_alpha = {
        "day": 0,
        "dawn": 12,
        "dusk": 20,
        "night": 24,
    }[phase]
    phase_alpha += round(abs(profile.temperature_bias) * 8)

    weather_alpha = {
        "clear": 0,
        "cloudy": 18,
        "rain": 24,
    }[weather]
    weather_alpha = round(weather_alpha * profile.weather_response)

    return ResolvedSpaceAppearance(
        floor_a=_respond(floor_seed, phase, weather, profile, 1.04),
        floor_b=_respond(floor_alt_seed, phase, weather, profile, 1.00),
        floor_edge=_respond(visual.structure, phase, weather, profile, .90),
        surface=_respond(visual.surface, phase, weather, profile, 1.08),
        material=_respond(visual.material, phase, weather, profile, .98),
        structure=_respond(visual.structure, phase, weather, profile, .88),
        circulation=_respond(circulation_seed, phase, weather, profile, 1.03),
        glass=_respond(glass_seed, phase, weather, profile, 1.12),
        vegetation=_respond(visual.vegetation, phase, weather, profile, .96),
        ambient=_respond(visual.ambient, phase, weather, profile, 1.06),
        accent=_respond(visual.accent, phase, weather, profile, 1.04),
        label=_respond(visual.label, phase, weather, profile, 1.02),
        glass_opacity=profile.glass_opacity,
        phase_wash=_hex(PHASE_TINT[phase]),
        phase_wash_alpha=max(0, min(64, phase_alpha)),
        weather_wash=_hex(WEATHER_TINT[weather]),
        weather_wash_alpha=max(0, min(64, weather_alpha)),
    )
