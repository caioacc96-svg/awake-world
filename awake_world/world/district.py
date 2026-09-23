from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor

from awake_world.design.massing import MassingVolume, get_space_massing_profile
from awake_world.design.material_light import (
    ResolvedSpaceAppearance,
    get_space_material_light_profile,
    resolve_space_appearance,
)
from awake_world.design.visual_foundation import (
    VisualFoundationProfile,
    framed_scene_rect,
    get_space_visual_foundation_profile,
)
from awake_world.design.spatial_depth import (
    StairFlight,
    get_space_spatial_depth_profile,
)
from awake_world.world.items import (
    ArchitecturalPortalDoor,
    CollisionRect,
    InteractionAnchorItem,
    InteractionSpec,
    IsoArchitecturalBlock,
    IsoBlock,
    IsoSurfacePatch,
    PlantItem,
    ScreenItem,
    ZoneLabel,
)
from awake_world.world.room import BaseRoomScene
from awake_world.world.systems.spaces import SPACE_CATALOG
from awake_world.world.systems.subtle_life import get_subtle_life_profile
from awake_world.world.systems.surfaces import surfaces_for_space


def _q(color: str) -> QColor:
    return QColor(color)


def _framed_rect(space_id: str) -> QRectF:
    massing = get_space_massing_profile(space_id)
    foundation = get_space_visual_foundation_profile(space_id)
    return QRectF(*framed_scene_rect(massing.scene_rect, foundation))


def _add_architectural_ground(
    scene: BaseRoomScene,
    appearance: ResolvedSpaceAppearance,
    foundation: VisualFoundationProfile,
) -> None:
    """Continuous civic ground: no checkerboard/debug-grid visual language."""

    p = scene.projector
    border = foundation.ground_border

    # A shallow site plinth gives the diorama a deliberate architectural edge.
    site_plinth = IsoBlock(
        p,
        -border,
        -border,
        scene.width_tiles + border * 2.0,
        scene.depth_tiles + border * 2.0,
        .10,
        _q(appearance.floor_edge).lighter(106),
        _q(appearance.structure).darker(112),
        _q(appearance.structure).darker(118),
        z=-.13,
    )
    site_plinth.setZValue(-12000)
    scene.addItem(site_plinth)

    ground = IsoSurfacePatch(
        p,
        0.0,
        0.0,
        float(scene.width_tiles),
        float(scene.depth_tiles),
        _q(appearance.floor_a),
        _q(appearance.floor_edge).lighter(108),
        z=.002,
    )
    ground.setZValue(-11000)
    scene.addItem(ground)

    # Large-format architectural joints replace per-tile checkerboarding.
    seam = _q(appearance.floor_edge).darker(104)
    spacing = foundation.joint_spacing
    for x in range(spacing, scene.width_tiles, spacing):
        joint = IsoSurfacePatch(
            p, x - .018, 0.0, .036, float(scene.depth_tiles),
            seam, None, z=.006, opacity=.22,
        )
        joint.setZValue(-10900)
        scene.addItem(joint)
    for y in range(spacing, scene.depth_tiles, spacing):
        joint = IsoSurfacePatch(
            p, 0.0, y - .018, float(scene.width_tiles), .036,
            seam, None, z=.006, opacity=.22,
        )
        joint.setZValue(-10900)
        scene.addItem(joint)

    # Perimeter inlay visually binds every environment to the same urban system.
    edge = _q(appearance.structure)
    for x, y, w, d in (
        (0.0, 0.0, scene.width_tiles, .10),
        (0.0, scene.depth_tiles - .10, scene.width_tiles, .10),
        (0.0, 0.0, .10, scene.depth_tiles),
        (scene.width_tiles - .10, 0.0, .10, scene.depth_tiles),
    ):
        perimeter = IsoSurfacePatch(p, x, y, w, d, edge, None, z=.009, opacity=.48)
        perimeter.setZValue(-10800)
        scene.addItem(perimeter)


def _add_circulation(
    scene: BaseRoomScene,
    appearance: ResolvedSpaceAppearance,
    primary_opacity: float = .78,
) -> None:
    massing = get_space_massing_profile(scene.room_id)
    p = scene.projector
    for index, band in enumerate(massing.circulation):
        path = IsoSurfacePatch(
            p,
            band.x,
            band.y,
            band.w,
            band.d,
            _q(appearance.circulation).lighter(104 if index == 0 else 101),
            _q(appearance.floor_edge).lighter(112),
            z=.014,
            opacity=primary_opacity if index == 0 else primary_opacity * .78,
        )
        path.setZValue(-7000 + index)
        scene.addItem(path)


def _add_stair_flight(
    scene: BaseRoomScene,
    stair: StairFlight,
    appearance: ResolvedSpaceAppearance,
) -> None:
    """Render a real stepped volume tied to a raised plane."""

    p = scene.projector
    step_run = stair.run / stair.steps
    for index in range(stair.steps):
        # stair.x/y is the high edge touching the platform. Each following
        # tread moves outward and drops toward grade.
        height = stair.rise * (stair.steps - index) / stair.steps
        offset = step_run * index
        if stair.axis == "y":
            x = stair.x
            y = stair.y + stair.direction * offset
            w = stair.width
            d = step_run + .025
        else:
            x = stair.x + stair.direction * offset
            y = stair.y
            w = step_run + .025
            d = stair.width
        scene.addItem(
            IsoArchitecturalBlock(
                p,
                x,
                y,
                w,
                d,
                height,
                _q(appearance.surface).lighter(112 - index),
                _q(appearance.material).lighter(103),
                _q(appearance.structure).darker(108),
            )
        )

        # Thin nosing makes each riser legible at isometric scale.
        nosing_h = min(.018, height * .24)
        if stair.axis == "y":
            nx = x
            ny = y + stair.direction * max(0.0, d - .035)
            nw = w
            nd = .045
        else:
            nx = x + stair.direction * max(0.0, w - .035)
            ny = y
            nw = .045
            nd = d
        scene.addItem(
            IsoArchitecturalBlock(
                p,
                nx,
                ny,
                nw,
                nd,
                nosing_h,
                _q(appearance.structure).lighter(116),
                _q(appearance.structure),
                _q(appearance.structure).darker(110),
                z=height,
                opacity=.88,
            )
        )


def _add_spatial_depth(
    scene: BaseRoomScene,
    appearance: ResolvedSpaceAppearance,
) -> None:
    """MVD-2.2: add authored elevation, stairs and structural support."""

    p = scene.projector
    profile = get_space_spatial_depth_profile(scene.room_id)

    for plane in profile.planes:
        if plane.kind in {"garden_step", "plant_terrace", "garden_edge"}:
            top = _q(appearance.floor_a).lighter(106)
        elif plane.kind in {"sunken_ring", "inner_ring", "social_core"}:
            top = _q(appearance.material).darker(102)
        else:
            top = _q(appearance.surface).lighter(107)

        scene.addItem(
            IsoArchitecturalBlock(
                p,
                plane.x,
                plane.y,
                plane.w,
                plane.d,
                plane.h,
                top,
                _q(appearance.material),
                _q(appearance.structure).darker(106),
            )
        )

        # Thin inset on top prevents a raised plane from reading as a plain box.
        inset = min(.16, plane.w * .08, plane.d * .12)
        if plane.w > inset * 2.0 and plane.d > inset * 2.0:
            scene.addItem(
                IsoSurfacePatch(
                    p,
                    plane.x + inset,
                    plane.y + inset,
                    plane.w - inset * 2.0,
                    plane.d - inset * 2.0,
                    _q(appearance.circulation).lighter(105),
                    _q(appearance.floor_edge).lighter(112),
                    z=plane.h + .006,
                    opacity=.72,
                )
            )

    for stair in profile.stairs:
        _add_stair_flight(scene, stair, appearance)

    for line in profile.piers:
        for index in range(line.count):
            x = line.x + line.dx * index
            y = line.y + line.dy * index
            scene.addItem(
                IsoArchitecturalBlock(
                    p,
                    x,
                    y,
                    line.w,
                    line.d,
                    line.h,
                    _q(appearance.structure).lighter(112),
                    _q(appearance.structure),
                    _q(appearance.structure).darker(112),
                )
            )


def _volume_colors(
    volume: MassingVolume,
    appearance: ResolvedSpaceAppearance,
    glass_landmark: bool,
) -> tuple[QColor, QColor, QColor, float]:
    surface = _q(appearance.surface)
    material = _q(appearance.material)
    structure = _q(appearance.structure)

    if volume.role == "landmark" and glass_landmark:
        return (
            _q(appearance.glass).lighter(112),
            _q(appearance.glass),
            structure.darker(104),
            appearance.glass_opacity,
        )
    if volume.role == "landmark":
        return surface.lighter(116), material.lighter(108), structure, 1.0
    if volume.role == "primary":
        return surface.lighter(109), material, structure.darker(104), 1.0
    return surface.lighter(104), material.lighter(102), structure.lighter(102), 1.0


def _add_facade_rhythm(
    scene: BaseRoomScene,
    volume: MassingVolume,
    foundation: VisualFoundationProfile,
    appearance: ResolvedSpaceAppearance,
    body_inset: float,
    plinth_h: float,
    cap_h: float,
) -> None:
    """Window bands + mullions make massing read as architecture, not boxes."""

    if volume.h < .82 or volume.w < .85 or volume.d < .42:
        return

    p = scene.projector
    available_h = max(.18, volume.h - plinth_h - cap_h)
    window_h = min(available_h * .72, max(.30, available_h * foundation.glazing_ratio))
    window_z = plinth_h + available_h * .22
    if window_z + window_h > volume.h - cap_h - .035:
        window_h = max(.16, volume.h - cap_h - .035 - window_z)

    front_margin = min(.24, volume.w * .16)
    front_w = volume.w - body_inset * 2.0 - front_margin * 2.0
    glass = _q(appearance.glass)
    frame = _q(appearance.structure).darker(106)

    if front_w > .34:
        front_x = volume.x + body_inset + front_margin
        front_y = volume.y + volume.d - body_inset - .045
        scene.addItem(
            IsoArchitecturalBlock(
                p, front_x, front_y, front_w, .085, window_h,
                glass.lighter(108), glass, frame,
                z=window_z,
                opacity=min(.94, appearance.glass_opacity + .06),
                glass=True,
            )
        )
        bays = max(2, min(foundation.facade_bays, round(front_w / .55) + 1))
        for bay in range(1, bays):
            mx = front_x + front_w * bay / bays
            scene.addItem(
                IsoBlock(
                    p, mx - .016, front_y - .008, .032, .10, window_h + .025,
                    frame.lighter(105), frame, frame.darker(108),
                    z=max(.02, window_z - .012),
                )
            )

    side_margin = min(.22, volume.d * .17)
    side_d = volume.d - body_inset * 2.0 - side_margin * 2.0
    if side_d > .40 and volume.w > .7:
        side_x = volume.x + volume.w - body_inset - .045
        side_y = volume.y + body_inset + side_margin
        scene.addItem(
            IsoArchitecturalBlock(
                p, side_x, side_y, .085, side_d, window_h,
                glass.lighter(106), glass.darker(102), frame,
                z=window_z,
                opacity=min(.93, appearance.glass_opacity + .04),
                glass=True,
            )
        )


def _add_architectural_volume(
    scene: BaseRoomScene,
    volume: MassingVolume,
    appearance: ResolvedSpaceAppearance,
    foundation: VisualFoundationProfile,
    glass_landmark: bool,
) -> None:
    """Layer a canonical MVD-1 volume into an authored architectural assembly."""

    p = scene.projector
    depth_profile = get_space_spatial_depth_profile(scene.room_id)

    # Contact shadow is a real projected footprint, not a global post-process.
    shadow = IsoSurfacePatch(
        p,
        volume.x + foundation.shadow_offset,
        volume.y + foundation.shadow_offset * .72,
        volume.w,
        volume.d,
        QColor("#12171A"),
        None,
        z=.010,
        opacity=foundation.shadow_opacity,
    )
    shadow.setZValue(-6000)
    scene.addItem(shadow)

    top, left, right, opacity = _volume_colors(volume, appearance, glass_landmark)

    plinth_h = min(foundation.plinth_height, max(.025, volume.h * .18))
    cap_h = min(foundation.cap_height, max(.020, volume.h * .10))
    body_h = max(.05, volume.h - plinth_h - cap_h)
    max_inset = max(.0, min(volume.w, volume.d) * .16)
    body_inset = min(foundation.body_inset, max_inset)
    if volume.w - body_inset * 2.0 < .08 or volume.d - body_inset * 2.0 < .08:
        body_inset = 0.0

    # Darker plinth anchors the volume and fixes the previous floating-box read.
    scene.addItem(
        IsoArchitecturalBlock(
            p,
            volume.x,
            volume.y,
            volume.w,
            volume.d,
            plinth_h,
            _q(appearance.material).darker(103),
            _q(appearance.structure).darker(108),
            _q(appearance.structure).darker(114),
        )
    )

    body_x = volume.x + body_inset
    body_y = volume.y + body_inset
    body_w = volume.w - body_inset * 2.0
    body_d = volume.d - body_inset * 2.0
    split_body = (
        volume.role in {"primary", "landmark"}
        and volume.h >= 2.1
        and body_w >= 1.35
        and body_d >= .72
    )
    if split_body:
        reveal_h = min(depth_profile.floor_reveal, body_h * .12)
        lower_h = max(.08, body_h * depth_profile.split_ratio)
        upper_h = max(.06, body_h - lower_h - reveal_h)
        extra_inset = min(
            depth_profile.upper_setback,
            max(.0, min(body_w, body_d) * .13),
        )

        scene.addItem(
            IsoArchitecturalBlock(
                p,
                body_x,
                body_y,
                body_w,
                body_d,
                lower_h,
                top,
                left,
                right,
                z=plinth_h,
                opacity=opacity,
                glass=glass_landmark,
            )
        )
        scene.addItem(
            IsoArchitecturalBlock(
                p,
                body_x - .025,
                body_y - .025,
                body_w + .05,
                body_d + .05,
                reveal_h,
                _q(appearance.surface).lighter(116),
                _q(appearance.material).lighter(106),
                _q(appearance.structure),
                z=plinth_h + lower_h,
                opacity=.94,
            )
        )
        scene.addItem(
            IsoArchitecturalBlock(
                p,
                body_x + extra_inset,
                body_y + extra_inset,
                max(.08, body_w - extra_inset * 2.0),
                max(.08, body_d - extra_inset * 2.0),
                upper_h,
                top.lighter(104),
                left.lighter(103),
                right,
                z=plinth_h + lower_h + reveal_h,
                opacity=opacity,
                glass=glass_landmark,
            )
        )
    else:
        scene.addItem(
            IsoArchitecturalBlock(
                p,
                body_x,
                body_y,
                body_w,
                body_d,
                body_h,
                top,
                left,
                right,
                z=plinth_h,
                opacity=opacity,
                glass=glass_landmark,
            )
        )

    _add_facade_rhythm(
        scene,
        volume,
        foundation,
        appearance,
        body_inset,
        plinth_h,
        cap_h,
    )

    # A thin shadow line before the roof slab creates depth with very little geometry.
    if volume.h > .42:
        scene.addItem(
            IsoBlock(
                p,
                body_x - .025,
                body_y - .025,
                body_w + .05,
                body_d + .05,
                .035,
                _q(appearance.structure).darker(112),
                _q(appearance.structure).darker(116),
                _q(appearance.structure).darker(120),
                z=max(plinth_h, volume.h - cap_h - .035),
                opacity=.82,
            )
        )

    overhang = min(foundation.cap_overhang, max(.015, min(volume.w, volume.d) * .14))
    scene.addItem(
        IsoArchitecturalBlock(
            p,
            volume.x - overhang,
            volume.y - overhang,
            volume.w + overhang * 2.0,
            volume.d + overhang * 2.0,
            cap_h,
            _q(appearance.surface).lighter(114),
            _q(appearance.material).lighter(105),
            _q(appearance.structure),
            z=max(.0, volume.h - cap_h),
        )
    )

    if (
        volume.role in {"primary", "landmark"}
        and volume.w >= 2.4
        and volume.d >= .85
        and volume.h >= 1.2
    ):
        lightbox_w = min(1.25, volume.w * .28)
        lightbox_d = min(.38, volume.d * .30)
        lightbox_x = volume.x + volume.w * .66 - lightbox_w / 2.0
        lightbox_y = volume.y + volume.d * .48 - lightbox_d / 2.0
        roof_glass = _q(appearance.glass)
        scene.addItem(
            IsoArchitecturalBlock(
                p,
                lightbox_x,
                lightbox_y,
                lightbox_w,
                lightbox_d,
                .075,
                roof_glass.lighter(116),
                roof_glass.lighter(105),
                _q(appearance.structure),
                z=volume.h + .015,
                opacity=min(.90, appearance.glass_opacity + .10),
                glass=True,
            )
        )

    if foundation.accent_inlay and volume.role in {"primary", "landmark"} and volume.h > .55:
        band = _q(appearance.accent).darker(122)
        scene.addItem(
            IsoBlock(
                p,
                body_x,
                body_y + max(.0, body_d - .055),
                body_w,
                .055,
                .035,
                band.lighter(106),
                band,
                band.darker(108),
                z=max(plinth_h, volume.h - cap_h - .11),
                opacity=.68,
            )
        )

    scene.collisions.append(
        CollisionRect(volume.x, volume.y, volume.w, volume.d, .055)
    )


def _add_massing(
    scene: BaseRoomScene,
    appearance: ResolvedSpaceAppearance,
) -> None:
    massing = get_space_massing_profile(scene.room_id)
    foundation = get_space_visual_foundation_profile(scene.room_id)
    material_profile = get_space_material_light_profile(scene.room_id)
    glass_landmark = material_profile.glass_mode in {"framed", "full"}

    for volume in massing.volumes:
        _add_architectural_volume(
            scene,
            volume,
            appearance,
            foundation,
            glass_landmark=glass_landmark and volume.role == "landmark",
        )


def _add_landscape(
    scene: BaseRoomScene,
    appearance: ResolvedSpaceAppearance,
) -> None:
    """Architectural planting with bounded MVD-3 micro-motion."""

    massing = get_space_massing_profile(scene.room_id)
    foundation = get_space_visual_foundation_profile(scene.room_id)
    life = get_subtle_life_profile(scene.room_id)
    p = scene.projector
    green = _q(appearance.vegetation)
    offsets = ((.0, .0, 1.0), (.24, -.12, .66), (-.20, .15, .58))

    for cluster_index, (x, y, scale) in enumerate(massing.vegetation_points):
        scene.addItem(
            IsoSurfacePatch(
                p,
                x - .36 * scale,
                y - .26 * scale,
                .72 * scale,
                .52 * scale,
                green.darker(132),
                _q(appearance.floor_edge),
                z=.018,
                opacity=.34,
            )
        )
        for layer_index, (dx, dy, layer_scale) in enumerate(offsets[:foundation.landscape_layers]):
            plant = PlantItem(
                p,
                x + dx * scale,
                y + dy * scale,
                green.lighter(100 + round((1.0 - layer_scale) * 14)),
                scale * layer_scale,
                motion_phase=cluster_index * .83 + layer_index * .57,
                motion_amplitude=life.vegetation_amplitude_deg,
                motion_speed=life.vegetation_speed,
            )
            scene.addItem(plant)
            scene.register_animation(plant)


def _add_subtle_life(
    scene: BaseRoomScene,
    appearance: ResolvedSpaceAppearance,
) -> None:
    """MVD-3 authored occupancy evidence and functional architectural state."""

    profile = get_subtle_life_profile(scene.room_id)
    p = scene.projector
    material = _q(appearance.material)
    accent = _q(appearance.accent)
    for index, trace in enumerate(profile.occupancy_traces):
        top = material.lighter(118 + (index % 2) * 5)
        side = material.darker(108)
        w = .18 * trace.scale
        d = .13 * trace.scale
        h = .05 if trace.kind in {"paper", "notebook", "tablet"} else .09
        scene.addItem(
            IsoArchitecturalBlock(
                p,
                trace.x - w / 2,
                trace.y - d / 2,
                w,
                d,
                h,
                top,
                side,
                side.darker(106),
                z=.02,
                opacity=.88,
            )
        )

    for anchor in profile.state_anchors:
        screen = ScreenItem(p, anchor.x, anchor.y, accent, anchor.scale)
        screen.set_active(True)
        scene.addItem(screen)
        scene.register_animation(screen)


def _add_traversal_guardrails(
    scene: BaseRoomScene,
    appearance: ResolvedSpaceAppearance,
) -> None:
    """MVD-6 visual safety language around authored raised walkable planes."""

    profile = get_space_spatial_depth_profile(scene.room_id)
    p = scene.projector
    rail = _q(appearance.structure).lighter(108)
    for plane in profile.planes:
        if plane.w < 2.2 or plane.d < .9:
            continue
        scene.addItem(
            IsoArchitecturalBlock(
                p, plane.x, plane.y, plane.w, .045, .28,
                rail.lighter(108), rail, rail.darker(108),
                z=plane.h, opacity=.76,
            )
        )
        scene.addItem(
            IsoArchitecturalBlock(
                p, plane.x + plane.w - .045, plane.y, .045, plane.d, .28,
                rail.lighter(108), rail, rail.darker(108),
                z=plane.h, opacity=.76,
            )
        )


def _add_surface_interactions(
    scene: BaseRoomScene,
    appearance: ResolvedSpaceAppearance,
) -> None:
    """MVD-4/MVD-7: work and social utility lives on physical world surfaces."""

    p = scene.projector
    accent = _q(appearance.accent)
    for surface in surfaces_for_space(scene.room_id):
        spec = InteractionSpec(
            surface.id,
            surface.x,
            surface.y,
            1.05,
            surface.role.value.upper(),
            surface.label or surface.kind.replace("_", " ").title(),
            "E  engage",
            surface.action,
            surface.id,
            surface.x,
            surface.y,
            0.0,
            -1.0,
            surface.z,
            surface.priority,
            surface.kind,
        )
        scene.interactions.append(spec)
        acknowledgement = InteractionAnchorItem(
            p, surface.x, surface.y, surface.z, accent
        )
        scene.interaction_acknowledgements[surface.id] = acknowledgement
        scene.addItem(acknowledgement)

def _add_signature_details(
    scene: BaseRoomScene,
    appearance: ResolvedSpaceAppearance,
) -> None:
    """Space-specific microarchitecture using one shared low-cost kit."""

    p = scene.projector
    structure = _q(appearance.structure)
    surface = _q(appearance.surface)
    material = _q(appearance.material)
    glass = _q(appearance.glass)

    def beam(
        x: float,
        y: float,
        w: float,
        d: float,
        z: float,
        h: float = .08,
        use_glass: bool = False,
    ) -> None:
        scene.addItem(
            IsoArchitecturalBlock(
                p,
                x,
                y,
                w,
                d,
                h,
                (glass.lighter(112) if use_glass else surface.lighter(108)),
                (glass if use_glass else material),
                structure,
                z=z,
                opacity=(min(.88, appearance.glass_opacity + .08) if use_glass else .96),
                glass=use_glass,
            )
        )

    if scene.room_id == "central_plaza":
        for index in range(5):
            beam(7.56, 5.48 + index * .58, 2.72, .085, 2.34, .075)
        beam(8.17, 5.30, .10, 2.82, 2.28, .09)
        beam(9.55, 5.30, .10, 2.82, 2.28, .09)

    elif scene.room_id == "observatory":
        for index in range(5):
            beam(6.56, 1.02 + index * .45, 3.82, .075, 3.02, .07)
        beam(7.16, .82, .085, 2.10, 2.94, .09)
        beam(9.72, .82, .085, 2.10, 2.94, .09)

    elif scene.room_id == "grid":
        for index in range(6):
            beam(4.78 + index * .70, 5.23, .045, .16, .58, 2.22)
        beam(4.62, 5.20, 4.25, .08, 2.78, .08, use_glass=True)

    elif scene.room_id == "twin_core":
        beam(1.72, 1.18, 1.45, .55, 3.26, .10, use_glass=True)
        beam(13.02, 1.18, 1.45, .55, 3.26, .10, use_glass=True)
        beam(7.10, 3.96, 3.82, .14, 1.00, .075, use_glass=True)

    elif scene.room_id == "trinity_lab":
        beam(7.48, 1.10, 2.90, .36, 3.05, .09, use_glass=True)
        for index in range(3):
            beam(7.05 + index * 1.35, 8.16, .82, .45, 1.00, .07, use_glass=True)

    elif scene.room_id == "garage":
        for index in range(6):
            beam(5.48 + index * .86, 1.05, .055, .12, .46, 2.72)
        beam(5.34, 1.03, 5.32, .08, 3.18, .08)

    elif scene.room_id == "kawaii_garden":
        for index in range(6):
            beam(6.36, 4.48 + index * .46, 3.38, .075, 2.24, .07)
        beam(6.72, 4.35, .08, 2.62, 2.18, .08)
        beam(9.30, 4.35, .08, 2.62, 2.18, .08)

    elif scene.room_id == "pit":
        beam(5.04, 4.13, 5.92, .09, .61, .055)
        beam(5.70, 4.93, 4.60, .09, .44, .050)
        beam(6.38, 6.05, 3.24, .09, .28, .045)

    elif scene.room_id == "glasshouse":
        for index in range(6):
            beam(5.90, 1.22 + index * .96, 5.18, .075, 2.72, .065, use_glass=True)
        beam(6.54, .94, .08, 6.10, 2.64, .08)
        beam(10.36, .94, .08, 6.10, 2.64, .08)

    elif scene.room_id == "quarter":
        # Repeated awnings make the district read as one urban system without
        # turning the civic spine into clutter.
        for volume in get_space_massing_profile("quarter").volumes:
            if volume.role != "primary" or volume.d < 1.2:
                continue
            awning_w = min(1.35, volume.w * .32)
            beam(
                volume.x + volume.w * .50 - awning_w / 2.0,
                volume.y + volume.d - .06,
                awning_w,
                .16,
                min(volume.h * .58, 1.48),
                .065,
                use_glass=True,
            )


class QuarterScene(BaseRoomScene):
    room_id = "quarter"
    room_label = "awake/quarter · living district"
    width_tiles = 24
    depth_tiles = 18
    spawn = (11.8, 15.5)

    PORTALS = {
        "observatory": (4.0, 3.4), "grid": (8.1, 2.8), "twin_core": (12.0, 2.5),
        "trinity_lab": (17.1, 3.3), "garage": (20.1, 7.2), "kawaii_garden": (19.0, 12.9),
        "pit": (14.5, 15.0), "glasshouse": (6.1, 14.2), "central_plaza": (11.7, 9.1),
    }

    def build_world(self) -> None:
        self.reset_scene()
        massing = get_space_massing_profile(self.room_id)
        appearance = resolve_space_appearance(self.room_id, self.phase, self.weather)
        foundation = get_space_visual_foundation_profile(self.room_id)
        _add_architectural_ground(self, appearance, foundation)
        _add_circulation(self, appearance, .82)
        _add_spatial_depth(self, appearance)
        _add_massing(self, appearance)
        _add_signature_details(self, appearance)
        _add_landscape(self, appearance)
        _add_subtle_life(self, appearance)
        _add_traversal_guardrails(self, appearance)
        _add_surface_interactions(self, appearance)
        p = self.projector

        for space_id, (x, y) in self.PORTALS.items():
            threshold_appearance = resolve_space_appearance(space_id, self.phase, self.weather)
            door = ArchitecturalPortalDoor(p, x, y, _q(threshold_appearance.accent))
            self.addItem(door)
            self.register_animation(door)
            definition = SPACE_CATALOG[space_id]
            self.interactions.append(
                InteractionSpec(
                    f"quarter.enter.{space_id}",
                    x, y + .55, 1.0,
                    "THRESHOLD", definition.name, "E  enter", "travel", space_id,
                )
            )

        self.add_npc("barista", [(10.2, 8.0), (11.0, 8.7), (10.3, 9.4)], .35)
        self.add_npc("courier", [(2.0, 8.3), (8.0, 8.3), (15.5, 8.3), (21.2, 8.3)], .64)
        self.add_npc("maintenance", [(12.1, 4.6), (13.0, 8.0), (12.2, 12.8)], .38)
        self.add_motes(
            [(2.0, 2.0, 1.1), (20.0, 3.0, 1.2), (4.0, 15.0, 1.0), (18.0, 14.5, 1.2)],
            _q(appearance.ambient),
        )
        self.addItem(
            ZoneLabel(
                "awake quarter · the living network",
                p.project(11.8, 16.8),
                _q(appearance.label),
            )
        )
        self.finish_build(_framed_rect(self.room_id), spawn=massing.spawn)


class AuthoredSpaceScene(BaseRoomScene):
    space_id = "observatory"
    exit_target = "quarter"

    @property
    def room_label(self) -> str:  # type: ignore[override]
        definition = SPACE_CATALOG[self.space_id]
        return f"awake/{self.space_id} · {definition.name.lower()}"

    @property
    def room_id(self) -> str:  # type: ignore[override]
        return self.space_id

    @property
    def width_tiles(self) -> int:  # type: ignore[override]
        return get_space_massing_profile(self.space_id).width_tiles

    @property
    def depth_tiles(self) -> int:  # type: ignore[override]
        return get_space_massing_profile(self.space_id).depth_tiles

    @property
    def spawn(self) -> tuple[float, float]:  # type: ignore[override]
        return get_space_massing_profile(self.space_id).spawn

    def palette(self) -> tuple[QColor, QColor, QColor, QColor]:
        appearance = resolve_space_appearance(self.space_id, self.phase, self.weather)
        return tuple(
            _q(color)
            for color in (
                appearance.surface,
                appearance.material,
                appearance.structure,
                appearance.accent,
            )
        )  # type: ignore[return-value]

    def _signature_interaction(self) -> tuple[float, float]:
        massing = get_space_massing_profile(self.space_id)
        landmarks = massing.landmark_volumes
        if landmarks:
            landmark = landmarks[-1]
            x = landmark.x + landmark.w / 2.0
            y = min(massing.depth_tiles - 2.15, landmark.y + landmark.d + .85)
            return x, y
        band = massing.circulation[0]
        return band.x + band.w / 2.0, band.y + band.d / 2.0

    def build_world(self) -> None:
        self.reset_scene()
        massing = get_space_massing_profile(self.space_id)
        appearance = resolve_space_appearance(self.space_id, self.phase, self.weather)
        foundation = get_space_visual_foundation_profile(self.space_id)
        _add_architectural_ground(self, appearance, foundation)
        _add_circulation(self, appearance)
        _add_spatial_depth(self, appearance)
        _add_massing(self, appearance)
        _add_signature_details(self, appearance)
        _add_landscape(self, appearance)
        _add_subtle_life(self, appearance)
        _add_traversal_guardrails(self, appearance)
        _add_surface_interactions(self, appearance)
        p = self.projector
        definition = SPACE_CATALOG[self.space_id]

        if self.space_id == "kawaii_garden":
            self.add_npc(
                "momo",
                [(4.0, 8.8), (7.0, 9.4), (11.4, 8.8), (9.4, 6.8)],
                .44,
            )
        if self.space_id == "central_plaza":
            self.add_npc(
                "barista",
                [(3.2, 5.0), (4.0, 6.0), (3.3, 7.0)],
                .34,
            )

        signature_x, signature_y = self._signature_interaction()
        self.interactions.append(
            InteractionSpec(
                f"{self.space_id}.signature",
                signature_x, signature_y, 1.3,
                "SPACE",
                f"Read {definition.name}",
                "E  inspect",
                "inspect",
            )
        )

        exit_x = massing.width_tiles / 2.0
        exit_y = massing.depth_tiles - 1.15
        exit_door = ArchitecturalPortalDoor(p, exit_x, exit_y, _q(appearance.accent))
        self.addItem(exit_door)
        self.register_animation(exit_door)
        self.interactions.append(
            InteractionSpec(
                f"{self.space_id}.exit",
                exit_x, exit_y - .15, 1.15,
                "THRESHOLD",
                "Return to Awake Quarter",
                "E  exit",
                "travel",
                self.exit_target,
            )
        )
        self.addItem(
            ZoneLabel(
                definition.name,
                p.project(exit_x, massing.depth_tiles - .35),
                _q(appearance.label),
            )
        )
        self.finish_build(_framed_rect(self.space_id), spawn=massing.spawn)


class ObservatoryScene(AuthoredSpaceScene):
    space_id = "observatory"


class GridScene(AuthoredSpaceScene):
    space_id = "grid"


class TwinCoreScene(AuthoredSpaceScene):
    space_id = "twin_core"


class TrinityLabScene(AuthoredSpaceScene):
    space_id = "trinity_lab"


class GarageScene(AuthoredSpaceScene):
    space_id = "garage"


class KawaiiGardenScene(AuthoredSpaceScene):
    space_id = "kawaii_garden"


class PitScene(AuthoredSpaceScene):
    space_id = "pit"


class GlasshouseScene(AuthoredSpaceScene):
    space_id = "glasshouse"


class CentralPlazaScene(AuthoredSpaceScene):
    space_id = "central_plaza"


QUARTER_ROOM_TYPES = {
    "quarter": QuarterScene,
    "central_plaza": CentralPlazaScene,
    "observatory": ObservatoryScene,
    "grid": GridScene,
    "twin_core": TwinCoreScene,
    "trinity_lab": TrinityLabScene,
    "garage": GarageScene,
    "kawaii_garden": KawaiiGardenScene,
    "pit": PitScene,
    "glasshouse": GlasshouseScene,
}
