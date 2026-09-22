from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor

from awake_world.design.world_visuals import get_space_visual_profile
from awake_world.world.items import CollisionRect, InteractionSpec, IsoBlock, IsoSurfacePatch, PlantItem, PortalDoor, ZoneLabel
from awake_world.world.room import BaseRoomScene
from awake_world.world.systems.spaces import SPACE_CATALOG


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
        self.add_floor(profile.floor_family)
        p = self.projector
        green = QColor(profile.vegetation)
        # MVD-0: the district reads as one authored material system. Local identity appears at thresholds.
        for x, y, w, d in [(1.2,7.6,21.2,2.0),(10.6,1.0,2.3,16.0),(3.0,12.0,6.4,1.1),(15.0,5.2,6.0,1.1)]:
            self.addItem(IsoSurfacePatch(p,x,y,w,d,QColor(profile.structure).lighter(122),QColor(profile.structure).lighter(110),opacity=.92))
        for x,y,w,d,h in [(2.3,1.7,3.5,2.1,.9),(7.0,1.2,3.0,2.0,.8),(11.0,1.0,3.4,1.8,.75),(16.1,1.8,4.2,2.4,1.0),(18.4,5.8,3.5,2.3,.8),(12.8,13.7,3.7,2.3,.75),(4.4,13.0,3.4,2.0,.72)]:
            self.addItem(IsoBlock(p,x,y,w,d,h,QColor(profile.surface),QColor(profile.material),QColor(profile.structure)))
            self.collisions.append(CollisionRect(x,y,w,d,.08))
        for x,y in [(2,10.5),(4,9.7),(6.5,6.5),(8.4,11.7),(16.9,10.2),(20.8,10.7),(3.2,5.8),(21.1,14.7)]:
            plant=PlantItem(p,x,y,green,1.0); self.addItem(plant)
        for space_id,(x,y) in self.PORTALS.items():
            threshold_profile = get_space_visual_profile(space_id)
            door=PortalDoor(p,x,y,QColor(threshold_profile.accent)); self.addItem(door); self.register_animation(door)
            definition=SPACE_CATALOG[space_id]
            self.interactions.append(InteractionSpec(f"quarter.enter.{space_id}",x,y+0.55,1.0,"THRESHOLD",definition.name,"E  enter","travel",space_id))
        self.add_npc("barista",[(10.2,8.0),(11.0,8.7),(10.3,9.4)],.35)
        self.add_npc("courier",[(2.0,8.3),(8.0,8.3),(15.5,8.3),(21.2,8.3)],.64)
        self.add_npc("maintenance",[(12.1,4.6),(13.0,8.0),(12.2,12.8)],.38)
        self.add_motes([(2.0,2.0,1.1),(20.0,3.0,1.2),(4.0,15.0,1.0),(18.0,14.5,1.2)],QColor(profile.ambient))
        self.addItem(ZoneLabel("awake quarter · the living network",p.project(11.8,16.8),QColor(profile.label)))
        self.finish_build(QRectF(-1450,-620,2900,1900))


class AuthoredSpaceScene(BaseRoomScene):
    space_id = "observatory"
    exit_target = "quarter"
    width_tiles = 15
    depth_tiles = 11
    spawn = (7.3,8.9)

    @property
    def room_label(self) -> str:  # type: ignore[override]
        d=SPACE_CATALOG[self.space_id]; return f"awake/{self.space_id} · {d.name.lower()}"

    @property
    def room_id(self) -> str:  # type: ignore[override]
        return self.space_id

    def palette(self) -> tuple[QColor,QColor,QColor,QColor]:
        profile = get_space_visual_profile(self.space_id)
        return tuple(QColor(c) for c in (profile.surface, profile.material, profile.structure, profile.accent))  # type: ignore[return-value]

    def build_world(self) -> None:
        self.reset_scene()
        profile = get_space_visual_profile(self.space_id)
        self.add_floor(profile.floor_family)
        p=self.projector; base,wood,dark,accent=self.palette(); d=SPACE_CATALOG[self.space_id]
        self.addItem(IsoSurfacePatch(p,1.0,1.0,13.0,8.7,base.darker(103),base.darker(112),opacity=.74))
        # Architecture shell + functional furniture blocks. Each scene has a different composition, not merely recoloring.
        layouts={
            "observatory":[(1.1,1.0,3.2,1.0,.75),(9.7,1.0,4.0,1.0,.65),(5.0,3.2,5.3,1.2,.48)],
            "grid":[(1.2,1.3,2.0,6.8,.7),(4.4,1.5,8.8,.8,.55),(5.0,5.0,7.4,.8,.55)],
            "twin_core":[(1.1,1.0,4.4,1.1,.7),(9.4,1.0,4.4,1.1,.7),(5.7,3.6,3.5,1.4,.62),(2.0,6.3,11.0,.8,.45)],
            "trinity_lab":[(1.1,1.0,12.7,.8,.5),(1.3,3.0,4.0,1.0,.55),(9.2,3.0,4.0,1.0,.55),(5.1,6.1,5.0,1.2,.52)],
            "garage":[(1.1,1.0,12.5,1.0,.7),(1.2,3.2,3.8,1.2,.58),(8.4,5.4,4.4,1.0,.55),(2.4,6.5,3.0,1.2,.45)],
            "kawaii_garden":[(1.5,1.5,5.0,2.2,.65),(8.6,1.4,4.5,2.0,.55),(5.7,5.8,3.0,1.2,.42)],
            "pit":[(1.0,1.0,12.8,1.0,.8),(1.2,3.2,5.0,1.0,.6),(8.0,3.2,5.0,1.0,.6),(3.5,6.2,8.0,1.4,.45)],
            "glasshouse":[(1.2,1.0,12.6,.65,.45),(1.5,3.0,3.2,1.0,.48),(9.9,3.0,3.2,1.0,.48),(5.2,6.2,4.7,1.0,.42)],
            "central_plaza":[(1.1,1.0,3.5,.7,.38),(10.2,1.0,3.5,.7,.38),(5.5,5.0,4.0,1.1,.32)],
        }[self.space_id]
        for x,y,w,dd,h in layouts:
            self.addItem(IsoBlock(p,x,y,w,dd,h,wood.lighter(118),dark.lighter(112),dark))
            self.collisions.append(CollisionRect(x,y,w,dd,.06))
        if self.space_id in {"observatory","trinity_lab","kawaii_garden","glasshouse","central_plaza"}:
            for x,y in [(2.0,8.0),(12.5,7.8),(10.6,5.8)]: self.addItem(PlantItem(p,x,y,QColor(profile.vegetation),1.15))
        if self.space_id == "kawaii_garden":
            self.add_npc("momo",[(4.0,6.5),(7.0,7.2),(10.5,6.6),(8.8,4.7)],.44)
        if self.space_id == "central_plaza":
            self.add_npc("barista",[(3.2,3.2),(4.0,4.2),(3.3,5.3)],.34)
        # Two real interactions in every major space: signature object + exit.
        self.interactions.append(InteractionSpec(f"{self.space_id}.signature",7.2,4.8,1.2,"SPACE",f"Read {d.name}","E  inspect","inspect"))
        exit_door=PortalDoor(p,7.2,9.2,QColor(profile.accent)); self.addItem(exit_door); self.register_animation(exit_door)
        self.interactions.append(InteractionSpec(f"{self.space_id}.exit",7.2,9.0,1.15,"THRESHOLD","Return to Awake Quarter","E  exit","travel",self.exit_target))
        self.addItem(ZoneLabel(d.name,p.project(7.2,9.7),QColor(profile.label)))
        self.finish_build(QRectF(-950,-430,1900,1350))


class ObservatoryScene(AuthoredSpaceScene): space_id="observatory"
class GridScene(AuthoredSpaceScene): space_id="grid"
class TwinCoreScene(AuthoredSpaceScene): space_id="twin_core"
class TrinityLabScene(AuthoredSpaceScene): space_id="trinity_lab"
class GarageScene(AuthoredSpaceScene): space_id="garage"
class KawaiiGardenScene(AuthoredSpaceScene): space_id="kawaii_garden"
class PitScene(AuthoredSpaceScene): space_id="pit"
class GlasshouseScene(AuthoredSpaceScene): space_id="glasshouse"
class CentralPlazaScene(AuthoredSpaceScene): space_id="central_plaza"


QUARTER_ROOM_TYPES = {
    "quarter": QuarterScene, "central_plaza": CentralPlazaScene, "observatory": ObservatoryScene,
    "grid": GridScene, "twin_core": TwinCoreScene, "trinity_lab": TrinityLabScene, "garage": GarageScene,
    "kawaii_garden": KawaiiGardenScene, "pit": PitScene, "glasshouse": GlasshouseScene,
}
