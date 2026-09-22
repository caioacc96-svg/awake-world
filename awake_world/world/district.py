from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor

from awake_world.design.massing import get_space_massing_profile
from awake_world.design.material_light import (
    ResolvedSpaceAppearance,
    get_space_material_light_profile,
    resolve_space_appearance,
)
from awake_world.design.world_visuals import get_space_visual_profile
from awake_world.world.items import (
    CollisionRect,
    InteractionSpec,
    IsoBlock,
    IsoFloorTile,
    IsoSurfacePatch,
    PlantItem,
    PortalDoor,
    ZoneLabel,
)
from awake_world.world.room import BaseRoomScene
from awake_world.world.systems.spaces import SPACE_CATALOG


def _add_material_floor(scene: BaseRoomScene, appearance: ResolvedSpaceAppearance) -> None:
    """MVD-2 floor response shared by every Living Quarter environment."""

    for y in range(scene.depth_tiles):
        for x in range(scene.width_tiles):
            point = scene.projector.project(x, y)
            fill = QColor(appearance.floor_a if (x + y) % 2 == 0 else appearance.floor_b)
            scene.addItem(
                IsoFloorTile(
                    point,
                    scene.projector.m.tile_width,
                    scene.projector.m.tile_height,
                    fill,
                    QColor(appearance.floor_edge),
                )
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
        profile = get_space_visual_profile(self.room_id)
        massing = get_space_massing_profile(self.room_id)
        appearance = resolve_space_appearance(self.room_id, self.phase, self.weather)
        material_profile = get_space_material_light_profile(self.room_id)
        _add_material_floor(self, appearance)
        p = self.projector

        path_fill = QColor(appearance.circulation)
        path_edge = QColor(appearance.floor_edge).lighter(108)
        for band in massing.circulation:
            self.addItem(
                IsoSurfacePatch(
                    p, band.x, band.y, band.w, band.d,
                    path_fill, path_edge, opacity=.90,
                )
            )

        # MVD-2: hierarchy remains spatial, while surfaces now react to phase/weather.
        for volume in massing.volumes:
            opacity = 1.0
            if volume.role == "landmark" and material_profile.glass_mode in {"framed", "full"}:
                top = QColor(appearance.glass).lighter(106)
                side = QColor(appearance.glass).darker(106)
                right = QColor(appearance.structure)
                opacity = appearance.glass_opacity
            elif volume.role == "landmark":
                top = QColor(appearance.surface).lighter(116)
                side = QColor(appearance.material).lighter(106)
                right = QColor(appearance.structure)
            elif volume.role == "primary":
                top = QColor(appearance.surface).lighter(108)
                side = QColor(appearance.material)
                right = QColor(appearance.structure).darker(102)
            else:
                top = QColor(appearance.surface).lighter(103)
                side = QColor(appearance.material).darker(102)
                right = QColor(appearance.structure).lighter(103)
            self.addItem(
                IsoBlock(
                    p, volume.x, volume.y, volume.w, volume.d, volume.h,
                    top, side, right, opacity=opacity,
                )
            )
            self.collisions.append(
                CollisionRect(volume.x, volume.y, volume.w, volume.d, .08)
            )

        green = QColor(appearance.vegetation)
        for x, y, scale in massing.vegetation_points:
            self.addItem(PlantItem(p, x, y, green, scale))

        # Destination color is reserved for thresholds; massing does the recognition work.
        for space_id, (x, y) in self.PORTALS.items():
            threshold_appearance = resolve_space_appearance(space_id, self.phase, self.weather)
            door = PortalDoor(p, x, y, QColor(threshold_appearance.accent))
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
            QColor(appearance.ambient),
        )
        self.addItem(
            ZoneLabel(
                "awake quarter · the living network",
                p.project(11.8, 16.8),
                QColor(appearance.label),
            )
        )
        self.finish_build(QRectF(*massing.scene_rect), spawn=massing.spawn)


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
            QColor(color)
            for color in (
                appearance.surface,
                appearance.material,
                appearance.structure,
                appearance.accent,
            )
        )  # type: ignore[return-value]

    def _add_circulation(self) -> None:
        massing = get_space_massing_profile(self.space_id)
        appearance = resolve_space_appearance(self.space_id, self.phase, self.weather)
        p = self.projector
        for index, band in enumerate(massing.circulation):
            fill = QColor(appearance.circulation).lighter(104 if index == 0 else 100)
            self.addItem(
                IsoSurfacePatch(
                    p, band.x, band.y, band.w, band.d,
                    fill,
                    QColor(appearance.floor_edge).lighter(108),
                    opacity=.64 if index else .80,
                )
            )

    def _add_massing(self) -> None:
        massing = get_space_massing_profile(self.space_id)
        appearance = resolve_space_appearance(self.space_id, self.phase, self.weather)
        material_profile = get_space_material_light_profile(self.space_id)
        p = self.projector
        surface = QColor(appearance.surface)
        material = QColor(appearance.material)
        structure = QColor(appearance.structure)

        for volume in massing.volumes:
            opacity = 1.0
            if volume.role == "landmark" and material_profile.glass_mode in {"framed", "full"}:
                top = QColor(appearance.glass).lighter(106)
                left = QColor(appearance.glass)
                right = structure
                opacity = appearance.glass_opacity
            elif volume.role == "landmark":
                top = surface.lighter(116)
                left = material.lighter(108)
                right = structure
            elif volume.role == "primary":
                top = surface.lighter(108)
                left = material
                right = structure.darker(102)
            else:
                top = surface.lighter(103)
                left = material.lighter(103)
                right = structure.lighter(103)
            self.addItem(
                IsoBlock(
                    p, volume.x, volume.y, volume.w, volume.d, volume.h,
                    top, left, right, opacity=opacity,
                )
            )
            self.collisions.append(
                CollisionRect(volume.x, volume.y, volume.w, volume.d, .055)
            )

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
        profile = get_space_visual_profile(self.space_id)
        massing = get_space_massing_profile(self.space_id)
        appearance = resolve_space_appearance(self.space_id, self.phase, self.weather)
        _add_material_floor(self, appearance)
        p = self.projector
        definition = SPACE_CATALOG[self.space_id]

        # MVD-1 order matters: void first, then structure, then local life.
        self._add_circulation()
        self._add_massing()

        for x, y, scale in massing.vegetation_points:
            self.addItem(
                PlantItem(p, x, y, QColor(appearance.vegetation), scale)
            )

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
        exit_door = PortalDoor(p, exit_x, exit_y, QColor(appearance.accent))
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
                QColor(appearance.label),
            )
        )
        self.finish_build(QRectF(*massing.scene_rect), spawn=massing.spawn)


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
