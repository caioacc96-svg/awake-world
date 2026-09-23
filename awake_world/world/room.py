from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsScene

from awake_world.design.theme.engine import ThemeEngine
from awake_world.world.avatar import AvatarItem
from awake_world.world.iso import IsoProjector
from awake_world.world.items import (
    AmbientMoteItem,
    BeaconItem,
    CollisionRect,
    DecorAnchorItem,
    DecorItem,
    FloorLampItem,
    InteractionSpec,
    IsoBlock,
    IsoFloorTile,
    IsoSurfacePatch,
    PlantItem,
    PortalDoor,
    ScreenItem,
    ShelfItem,
    SlidingDoorItem,
    WallArtItem,
    ZoneLabel,
)
from awake_world.world.lighting import SceneLightWash, phase_for_minutes
from awake_world.world.environment import RainStreak, WeatherWash
from awake_world.world.state import WorldState
from awake_world.world.npc import NPCItem, NPC_PROFILES
from awake_world.world.progression import STARTER_DECOR, add_journal, unlock_decor
from awake_world.world.systems.interactions import InteractionSystem
from awake_world.world.systems.traversal import TraversalSystem


@dataclass(frozen=True)
class InteractionOutcome:
    message: str
    travel_to: str | None = None
    changed: bool = False
    rebuild: bool = False
    discovery: bool = False
    set_time: float | None = None


class BaseRoomScene(QGraphicsScene):
    room_id = "base"
    room_label = "awake/world"
    width_tiles = 12
    depth_tiles = 10
    spawn = (5.2, 7.2)

    def __init__(self, theme: ThemeEngine, state: WorldState) -> None:
        super().__init__()
        self.theme = theme
        self.state = state
        self.projector = IsoProjector()
        self.interactions: list[InteractionSpec] = []
        self.interaction_system = InteractionSystem()
        self.interaction_acknowledgements: dict[str, object] = {}
        self.collisions: list[CollisionRect] = []
        try:
            self.traversal: TraversalSystem | None = TraversalSystem(self.room_id)
        except KeyError:
            self.traversal = None
        self.stateful_items: dict[str, object] = {}
        self.animated_items: list[object] = []
        self.ambient_lights: list[FloorLampItem] = []
        self.npcs: dict[str, NPCItem] = {}
        self.transition_doors: dict[str, SlidingDoorItem] = {}
        self.world_minutes = float(state.world_minutes)
        self.phase = phase_for_minutes(self.world_minutes)
        self.light_wash: SceneLightWash | None = None
        self.weather_wash: WeatherWash | None = None
        self.rain_items: list[RainStreak] = []
        self.weather = getattr(state, "weather", "clear")
        self.avatar = AvatarItem(self.projector, QColor(theme.color("awake_blue")))
        self.build_world()
        self.state.visits[self.room_id] = self.state.visits.get(self.room_id, 0) + 1
        self.state.last_room = self.room_id

    def build_world(self) -> None:
        raise NotImplementedError

    def reset_scene(self) -> None:
        self.clear()
        self.interactions.clear()
        self.interaction_acknowledgements.clear()
        self.interaction_system.clear()
        self.collisions.clear()
        self.stateful_items.clear()
        self.animated_items.clear()
        self.ambient_lights.clear()
        self.npcs.clear()
        self.transition_doors.clear()
        self.light_wash = None
        self.weather_wash = None
        self.rain_items.clear()
        self.avatar = AvatarItem(self.projector, QColor(self.theme.color("awake_blue")))

    def phase_color(self, day: str, dawn: str | None = None, dusk: str | None = None, night: str | None = None) -> QColor:
        mapping = {
            "day": day,
            "dawn": dawn or day,
            "dusk": dusk or dawn or day,
            "night": night or dusk or dawn or day,
        }
        return QColor(mapping[self.phase])

    def add_floor(self, family: str = "warm") -> None:
        if family == "plaza":
            day_a, day_b, day_edge = "#DED8CD", "#D8D1C5", "#CBC3B7"
        elif family == "roof":
            day_a, day_b, day_edge = "#D4CEC1", "#CBC4B7", "#BFB7AA"
        elif family == "home":
            day_a, day_b, day_edge = "#E8E0D2", "#E2D9CA", "#D0C5B5"
        else:
            day_a, day_b, day_edge = "#E7E1D6", "#E1DACF", "#D2CBC0"

        if self.phase == "night":
            base_a, base_b, edge = QColor("#1D2330"), QColor("#202735"), QColor("#2A3241")
        elif self.phase == "dusk":
            base_a, base_b, edge = QColor(day_a).darker(106), QColor(day_b).darker(108), QColor(day_edge).darker(105)
        elif self.phase == "dawn":
            base_a, base_b, edge = QColor(day_a).lighter(103), QColor(day_b).lighter(102), QColor(day_edge)
        else:
            base_a, base_b, edge = QColor(day_a), QColor(day_b), QColor(day_edge)

        for y in range(self.depth_tiles):
            for x in range(self.width_tiles):
                p = self.projector.project(x, y)
                fill = base_a if (x + y) % 2 == 0 else base_b
                self.addItem(IsoFloorTile(p, self.projector.m.tile_width, self.projector.m.tile_height, fill, edge))

    def register_animation(self, item: object) -> object:
        self.animated_items.append(item)
        return item

    def register_light(self, lamp: FloorLampItem) -> FloorLampItem:
        self.ambient_lights.append(lamp)
        self.animated_items.append(lamp)
        self.addItem(lamp)
        return lamp

    def add_npc(self, key: str, waypoints: list[tuple[float, float]], speed: float = 0.48) -> NPCItem:
        npc = NPCItem(self.projector, NPC_PROFILES[key], waypoints, speed=speed)
        self.npcs[key] = npc
        self.addItem(npc)
        self.register_animation(npc)
        return npc

    def add_motes(self, points: list[tuple[float, float, float]], accent: QColor) -> None:
        for index, (x, y, radius) in enumerate(points):
            mote = AmbientMoteItem(self.projector.project(x, y, 0.55 + (index % 3) * 0.18), accent, phase=index * 0.71, radius=radius)
            self.addItem(mote)
            self.register_animation(mote)

    def finish_build(self, scene_rect: QRectF, spawn: tuple[float, float] | None = None) -> None:
        self.addItem(self.avatar)
        sx, sy = spawn or self.spawn
        self.avatar.set_grid_position(sx, sy, self.elevation_at(sx, sy))
        self.setSceneRect(scene_rect)
        self.apply_world_state()
        self.apply_phase_lighting()
        self.light_wash = SceneLightWash(scene_rect, self.phase, self.room_id)
        self.addItem(self.light_wash)
        self.apply_weather(self.weather, scene_rect)


    def apply_weather(self, weather: str, scene_rect: QRectF | None = None) -> None:
        self.weather = weather
        self.state.weather = weather
        if self.weather_wash is not None:
            self.removeItem(self.weather_wash)
            self.weather_wash = None
        for item in tuple(self.rain_items):
            if item.scene() is self:
                self.removeItem(item)
            if item in self.animated_items:
                self.animated_items.remove(item)
        self.rain_items.clear()
        rect = scene_rect or self.sceneRect()
        if rect.isNull():
            return
        self.weather_wash = WeatherWash(rect, weather, self.room_id, self.phase)
        self.addItem(self.weather_wash)
        if weather == "rain":
            for index in range(46):
                streak = RainStreak(rect, index)
                self.rain_items.append(streak)
                self.addItem(streak)
                self.register_animation(streak)

    def set_world_time(self, minutes: float, force: bool = False) -> None:
        minutes = float(minutes) % (24 * 60)
        new_phase = phase_for_minutes(minutes)
        self.world_minutes = minutes
        self.state.world_minutes = minutes
        if new_phase == self.phase and not force:
            if self.light_wash:
                self.light_wash.set_phase(new_phase)
            return

        current = (self.avatar.grid_x, self.avatar.grid_y)
        pose = self.avatar.pose
        facing = (self.avatar.facing.x(), self.avatar.facing.y())
        self.phase = new_phase
        self.build_world()
        current_z = self.elevation_at(*current)
        self.avatar.set_grid_position(current[0], current[1], current_z)
        if pose != "standing":
            self.avatar.set_pose(pose, current[0], current[1], facing[0], facing[1], current_z)

    def rebuild_preserving_avatar(self) -> None:
        current = (self.avatar.grid_x, self.avatar.grid_y)
        pose = self.avatar.pose
        facing = (self.avatar.facing.x(), self.avatar.facing.y())
        self.build_world()
        current_z = self.elevation_at(*current)
        self.avatar.set_grid_position(current[0], current[1], current_z)
        if pose != "standing":
            self.avatar.set_pose(pose, current[0], current[1], facing[0], facing[1], current_z)

    def apply_phase_lighting(self) -> None:
        active = self.phase in {"dusk", "night", "dawn"}
        for lamp in self.ambient_lights:
            lamp.set_active(active)

    def advance_ambient(self, dt: float) -> None:
        for item in tuple(self.animated_items):
            advance = getattr(item, "advance_animation", None)
            if callable(advance):
                advance(dt)

    def elevation_at(self, x: float, y: float) -> float:
        if self.traversal is None:
            return 0.0
        return self.traversal.elevation_at(x, y)

    def can_move_to(self, x: float, y: float, radius: float = 0.18) -> bool:
        if x < 0.35 or y < 0.35 or x > self.width_tiles - 0.35 or y > self.depth_tiles - 0.35:
            return False
        if any(rect.contains(x, y, radius) for rect in self.collisions):
            return False
        if self.traversal is not None and not self.traversal.can_transition(
            self.avatar.grid_x,
            self.avatar.grid_y,
            self.avatar.grid_z,
            x,
            y,
        ):
            return False
        return True

    def closest_interaction(self) -> InteractionSpec | None:
        candidates = list(self.interactions)
        candidates.extend(npc.interaction_spec() for npc in self.npcs.values())
        selected = self.interaction_system.nearest(
            candidates,
            self.avatar.grid_x,
            self.avatar.grid_y,
            (self.avatar.facing.x(), self.avatar.facing.y()),
            self.avatar.grid_z,
        )
        for key, item in self.interaction_acknowledgements.items():
            setter = getattr(item, "set_active", None)
            if callable(setter):
                setter(selected is not None and getattr(selected, "key", "") == key)
        return selected

    def _talk(self, npc_key: str) -> str:
        count = self.state.conversations.get(npc_key, 0)
        self.state.conversations[npc_key] = count + 1
        if npc_key == "mira":
            if count == 0:
                add_journal(self.state, "mira_intro")
                return "Mira · ‘A room should tell you what it can do before a panel does.’"
            if self.phase == "night":
                return "Mira · ‘At night the studio stops asking for attention. Keep it that way.’"
            return "Mira · ‘Try actually sitting at the project table. The world should meet you halfway.’"
        if npc_key == "sol":
            if count == 0:
                add_journal(self.state, "sol_intro")
                unlock_decor(self.state, "garden_stone")
                return "Sol · ‘Take this signal stone home. The commons grows better when pieces travel.’"
            return "Sol · ‘Nothing important happens at the kiosk. That is why people keep coming back.’"
        if npc_key == "echo":
            if count == 0:
                add_journal(self.state, "echo_intro")
                return "Echo · ‘The skyline is mostly unfinished messages pretending to be lights.’"
            if self.phase in {"dusk", "night"}:
                return "Echo · ‘Wake the listening deck after dusk. It remembers a different version of the rooftop.’"
            return "Echo · ‘Come back after the light changes.’"
        return "A quiet acknowledgement passes between you."

    def activate(self, spec: InteractionSpec) -> InteractionOutcome:
        first_time = spec.key not in self.state.discovered
        self.state.discovered.add(spec.key)

        if spec.action == "travel":
            door = self.transition_doors.get(spec.key)
            if door:
                door.set_open(True)
            destination = spec.target or "headquarters"
            return InteractionOutcome(
                f"Threshold opening · entering awake/{destination}",
                travel_to=destination,
                changed=first_time,
                discovery=first_time,
            )

        if spec.action == "toggle":
            value = not self.state.toggles.get(spec.key, False)
            self.state.toggles[spec.key] = value
            self.apply_world_state()
            return InteractionOutcome(
                f"{spec.eyebrow.title()} · {'online' if value else 'standby'}",
                changed=True,
                discovery=first_time,
            )

        if spec.action == "beacon":
            self.state.toggles[spec.key] = True
            self.apply_world_state()
            return InteractionOutcome(
                "Awake signal found · another corner of the network is lit",
                changed=True,
                discovery=first_time,
            )

        if spec.action in {"sit", "rest", "use", "listen"}:
            pose_map = {"sit": "seated", "rest": "resting", "use": "working", "listen": "listening"}
            if self.avatar.locked_in_pose:
                self.avatar.stand()
                return InteractionOutcome("Back on your feet", changed=False)
            ax = spec.anchor_x if spec.anchor_x is not None else spec.x
            ay = spec.anchor_y if spec.anchor_y is not None else spec.y
            self.avatar.set_pose(pose_map[spec.action], ax, ay, spec.facing_x, spec.facing_y, spec.z)
            if spec.action == "rest":
                if "first_rest" not in self.state.flags:
                    self.state.flags.add("first_rest")
                    add_journal(self.state, "first_rest")
                message = "Quiet mode · the world keeps moving around you"
            elif spec.action == "listen":
                self.state.toggles[spec.target or spec.key] = True
                self.apply_world_state()
                message = "Listening mode · the deck opens a wider field"
            else:
                if spec.action == "use" and spec.target:
                    self.state.toggles[spec.target] = True
                    self.apply_world_state()
                message = f"{spec.eyebrow.title()} · in use"
            return InteractionOutcome(message, changed=first_time, discovery=first_time)

        if spec.action == "surface":
            space_state = self.state.space_states.setdefault(self.room_id, {})
            occupancy = space_state.setdefault("surface_occupancy", {})
            if not isinstance(occupancy, dict):
                occupancy = {}
                space_state["surface_occupancy"] = occupancy
            members = [str(value) for value in occupancy.get(spec.target or spec.key, [])]
            if "local_player" not in members:
                members.append("local_player")
            occupancy[spec.target or spec.key] = members
            ax = spec.anchor_x if spec.anchor_x is not None else spec.x
            ay = spec.anchor_y if spec.anchor_y is not None else spec.y
            pose = "seated" if spec.surface_kind in {"sofa", "meeting_table", "arcade"} else "working"
            self.avatar.set_pose(pose, ax, ay, spec.facing_x, spec.facing_y, spec.z)
            return InteractionOutcome(
                f"{spec.eyebrow.title()} · {spec.title} · occupied",
                changed=True,
                discovery=first_time,
            )

        if spec.action == "talk":
            return InteractionOutcome(self._talk(spec.target or ""), changed=True, discovery=first_time)

        if spec.action == "decorate":
            anchor = spec.target or spec.key
            choices = [""] + sorted(self.state.inventory)
            current = self.state.decor.get(anchor, "")
            try:
                index = choices.index(current)
            except ValueError:
                index = 0
            next_key = choices[(index + 1) % len(choices)]
            if next_key:
                self.state.decor[anchor] = next_key
                return InteractionOutcome(
                    f"awake/home · {next_key.replace('_', ' ')} placed",
                    changed=True,
                    rebuild=True,
                    discovery=first_time,
                )
            self.state.decor.pop(anchor, None)
            return InteractionOutcome("awake/home · anchor cleared", changed=True, rebuild=True, discovery=first_time)

        if spec.action == "sleep":
            self.state.flags.add("slept_once")
            return InteractionOutcome(
                "Rest cycle complete · morning light returns",
                changed=True,
                discovery=first_time,
                set_time=7 * 60 + 30,
            )

        if spec.action == "inspect":
            authored = {
                "hq.collab": "Collab nook · the table is covered in deliberately unfinished diagrams",
                "plaza.kiosk": "Commons kiosk · the counter keeps a tiny archive of things people forgot to take",
                "home.window": "Window · the network looks warmer from inside a room that remembers you",
            }
            if spec.key in authored:
                return InteractionOutcome(authored[spec.key], changed=first_time, discovery=first_time)

        return InteractionOutcome(f"{spec.eyebrow.title()} · {spec.title}", changed=first_time, discovery=first_time)

    def apply_world_state(self) -> None:
        for key, item in self.stateful_items.items():
            state_key = key.removesuffix(".secondary")
            active = self.state.toggles.get(state_key, False)
            setter = getattr(item, "set_active", None)
            if callable(setter):
                setter(active)
        self.apply_phase_lighting()


class HeadquartersScene(BaseRoomScene):
    room_id = "headquarters"
    room_label = "awake/headquarters · living studio"
    width_tiles = 15
    depth_tiles = 12
    spawn = (7.0, 9.65)

    def build_world(self) -> None:
        self.reset_scene()
        self.add_floor("warm")
        p = self.projector

        # Architectural shell
        wall = self.phase_color("#F0EBE2", "#F1E7DB", "#D9C8B9", "#252C39")
        wall_side = self.phase_color("#D7D0C5", "#D9CEC0", "#BFAFA2", "#1C222D")
        self.addItem(IsoBlock(p, -0.35, -0.25, 15.7, 0.30, 2.65, wall, wall_side, wall_side))
        self.addItem(IsoBlock(p, -0.35, -0.05, 0.30, 12.35, 2.65, wall, wall_side, wall_side))

        # Warm studio inlays keep the large room from reading as a flat grid.
        rug = QColor("#C9B6A3") if self.phase != "night" else QColor("#313849")
        rug2 = QColor("#B9CFC2") if self.phase != "night" else QColor("#2A3B39")
        self.addItem(IsoSurfacePatch(p, 2.0, 2.35, 4.9, 3.65, rug, QColor("#B29C88"), opacity=0.82))
        self.addItem(IsoSurfacePatch(p, 8.25, 5.05, 4.4, 3.45, QColor("#D5C2B7") if self.phase != "night" else QColor("#3A3137"), opacity=0.88))
        self.addItem(IsoSurfacePatch(p, 1.65, 7.25, 4.25, 2.65, rug2, opacity=0.74))

        blue = QColor(self.theme.color("awake_blue"))
        mint = QColor(self.theme.color("living_mint"))
        coral = QColor(self.theme.color("dawn_coral"))
        gold = QColor(self.theme.color("signal_gold"))
        lilac = QColor(self.theme.color("dream_lilac"))
        wood = QColor(self.theme.color("wood"))
        wood_dark = QColor(self.theme.color("wood_dark"))
        graphite = QColor(self.theme.color("graphite"))
        plant = QColor(self.theme.color("plant"))
        glass = self.phase_color("#C7DDE0", "#D2E1DE", "#AFBEC5", "#4A6574")

        # Portal / entrance
        portal = PortalDoor(p, 7.45, 0.34, blue)
        self.addItem(portal)
        self.register_animation(portal)
        self.interactions.append(InteractionSpec(
            "hq.portal.plaza", 7.45, 1.18, 1.22,
            "PORTAL", "Enter awake/plaza", "E  cross portal", "travel", "plaza"
        ))

        # Windows + wall art
        for x in (1.45, 2.75, 10.95, 12.25):
            self.addItem(IsoBlock(p, x, 0.07, 0.82, 0.06, 1.65, glass.lighter(114), glass, glass.darker(110), z=0.48, opacity=0.82))
        self.addItem(WallArtItem(p, 5.2, 0.18, 1.58, coral, 0))
        self.addItem(WallArtItem(p, 9.15, 0.18, 1.58, mint, 1))

        # Project studio — floating table, not a solid game block.
        for lx, ly in ((2.65, 3.05), (5.35, 3.05), (2.65, 4.0), (5.35, 4.0)):
            self.addItem(IsoBlock(p, lx, ly, 0.18, 0.18, 0.66, graphite.lighter(108), graphite, graphite.darker(112)))
        self.addItem(IsoBlock(p, 2.48, 2.88, 3.35, 1.35, 0.12, wood.lighter(112), wood, wood_dark, z=0.66))
        self.collisions.append(CollisionRect(2.45, 2.82, 3.45, 1.48, padding=0.06))

        screen_a = ScreenItem(p, 3.35, 3.05, blue, 0.92)
        screen_b = ScreenItem(p, 4.75, 3.43, mint, 0.92)
        self.addItem(screen_a); self.addItem(screen_b)
        self.register_animation(screen_a); self.register_animation(screen_b)
        self.stateful_items["hq.project_table"] = screen_a
        self.stateful_items["hq.project_table.secondary"] = screen_b
        self.interactions.append(InteractionSpec(
            "hq.project_table", 4.25, 4.72, 1.48,
            "PROJECT TABLE", "Use the studio surface", "E  sit / stand", "use", "hq.project_table",
            4.25, 4.58, 0.0, -1.0
        ))
        self.addItem(ZoneLabel("project studio", p.project(4.2, 5.75), QColor("#676B76")))

        # Shelf and plant give the studio a residential/workplace edge.
        self.addItem(ShelfItem(p, 0.72, 4.25, blue))
        self.collisions.append(CollisionRect(0.45, 3.9, 0.7, 1.05, padding=0.04))
        self.addItem(PlantItem(p, 1.25, 5.55, plant, 1.08))
        self.collisions.append(CollisionRect(1.0, 5.3, 0.5, 0.5, padding=0.02))

        # Media wall — architectural console + active screen.
        self.addItem(IsoBlock(p, 9.25, 1.72, 3.25, 0.48, 0.42, graphite.lighter(110), graphite, graphite.darker(120)))
        media = ScreenItem(p, 10.85, 1.94, lilac, 1.16)
        self.addItem(media); self.register_animation(media)
        self.stateful_items["hq.media_wall"] = media
        self.interactions.append(InteractionSpec(
            "hq.media_wall", 10.9, 2.92, 1.40,
            "MEDIA WALL", "Bring the wall online", "E  toggle media wall", "toggle"
        ))
        self.collisions.append(CollisionRect(9.2, 1.62, 3.35, 0.64, padding=0.05))

        # Lounge: two low sofas, coffee table, floor lamp.
        self.addItem(IsoBlock(p, 8.6, 6.05, 2.35, 0.78, 0.34, coral.lighter(132), coral.lighter(112), coral.darker(108)))
        self.addItem(IsoBlock(p, 8.62, 6.07, 2.35, 0.18, 0.54, coral.lighter(120), coral, coral.darker(112), z=0.34))
        self.addItem(IsoBlock(p, 10.75, 5.0, 0.78, 2.15, 0.34, coral.lighter(132), coral.lighter(112), coral.darker(108)))
        self.addItem(IsoBlock(p, 11.35, 5.02, 0.18, 2.15, 0.54, coral.lighter(120), coral, coral.darker(112), z=0.34))
        self.addItem(IsoBlock(p, 8.75, 4.95, 1.45, 0.82, 0.18, wood.lighter(116), wood, wood_dark, z=0.20))
        self.collisions.extend([
            CollisionRect(8.55, 6.0, 2.45, 0.86, padding=0.04),
            CollisionRect(10.72, 4.96, 0.86, 2.25, padding=0.04),
            CollisionRect(8.7, 4.9, 1.55, 0.92, padding=0.04),
        ])
        self.interactions.append(InteractionSpec(
            "hq.lounge", 9.2, 7.48, 1.58,
            "LOUNGE", "Let the room slow down", "E  sit / stand", "rest", None,
            9.15, 7.05, 0.0, -1.0
        ))
        lamp = FloorLampItem(p, 12.0, 6.55, gold)
        self.register_light(lamp)
        self.collisions.append(CollisionRect(11.78, 6.32, 0.44, 0.44, padding=0.02))
        self.addItem(ZoneLabel("lounge", p.project(9.6, 8.25), QColor("#676B76")))

        # Collaboration nook — glass divider + soft seats.
        for x in (1.65, 2.75, 3.85, 4.95):
            self.addItem(IsoBlock(p, x, 6.85, 0.74, 0.055, 1.08, glass.lighter(116), glass, glass.darker(108), opacity=0.58))
        self.addItem(IsoBlock(p, 2.65, 7.82, 1.5, 0.85, 0.20, wood.lighter(116), wood, wood_dark, z=0.18))
        for x, y in ((1.95, 7.5), (4.25, 7.55), (2.15, 9.0), (4.15, 9.0)):
            self.addItem(IsoBlock(p, x, y, 0.58, 0.58, 0.34, mint.lighter(130), mint.lighter(110), mint.darker(110)))
            self.collisions.append(CollisionRect(x, y, 0.58, 0.58, padding=0.03))
        self.collisions.append(CollisionRect(2.62, 7.78, 1.58, 0.92, padding=0.03))
        self.interactions.append(InteractionSpec(
            "hq.collab", 3.1, 9.75, 1.25,
            "COLLAB NOOK", "A place for unfinished ideas", "E  inspect", "inspect"
        ))
        self.addItem(ZoneLabel("collab nook", p.project(3.15, 10.35), QColor("#676B76")))

        # Lift to rooftop expands the world without another portal-looking portal.
        self.addItem(IsoBlock(p, 13.35, 3.55, 1.05, 1.48, 1.92, graphite.lighter(115), graphite, graphite.darker(118)))
        self.addItem(IsoBlock(p, 13.48, 3.72, 0.76, 0.06, 1.45, glass.lighter(118), glass, glass.darker(108), z=0.18, opacity=0.42))
        lift_door = SlidingDoorItem(p, 13.78, 4.22, blue)
        self.addItem(lift_door); self.register_animation(lift_door)
        self.transition_doors["hq.lift.rooftop"] = lift_door
        self.collisions.append(CollisionRect(13.32, 3.52, 1.12, 1.55, padding=0.03))
        self.interactions.append(InteractionSpec(
            "hq.lift.rooftop", 12.75, 4.95, 1.18,
            "ROOFTOP LIFT", "Go above the noise", "E  take lift", "travel", "rooftop"
        ))

        # Hidden signal in a less obvious corner.
        signal = BeaconItem(p, 13.05, 9.85, gold, tall=True)
        self.addItem(signal); self.register_animation(signal)
        self.stateful_items["hq.signal"] = signal
        self.interactions.append(InteractionSpec(
            "hq.signal", 12.7, 10.15, 1.08,
            "AWAKE SIGNAL", "A dormant network light", "E  wake signal", "beacon"
        ))

        for x, y, s in ((1.0, 1.18, 1.0), (13.6, 1.2, 1.0), (0.95, 10.8, 1.08), (13.8, 10.7, 1.12)):
            self.addItem(PlantItem(p, x, y, plant, s))
            self.collisions.append(CollisionRect(x - 0.24, y - 0.24, 0.48, 0.48, padding=0.02))

        # Physical threshold into the private single-player space.
        home_door = SlidingDoorItem(p, 14.12, 7.75, blue)
        self.addItem(home_door); self.register_animation(home_door)
        self.transition_doors["hq.door.home"] = home_door
        self.interactions.append(InteractionSpec(
            "hq.door.home", 13.15, 8.05, 1.18,
            "PRIVATE THRESHOLD", "Enter awake/home", "E  open door", "travel", "home"
        ))

        self.add_npc("mira", [(6.25, 5.55), (7.55, 5.95), (6.7, 7.05), (5.9, 6.25)], speed=0.42)
        self.add_motes([(2.0,1.6,1.6),(3.1,1.45,1.4),(10.8,1.55,1.7),(12.1,1.35,1.3),(7.4,4.8,1.2)], gold)

        self.finish_build(QRectF(-1040, -370, 2080, 1390))


class PlazaScene(BaseRoomScene):
    room_id = "plaza"
    room_label = "awake/plaza · central commons"
    width_tiles = 17
    depth_tiles = 14
    spawn = (8.0, 11.65)

    def build_world(self) -> None:
        self.reset_scene()
        self.add_floor("plaza")
        p = self.projector

        blue = QColor(self.theme.color("awake_blue"))
        mint = QColor(self.theme.color("living_mint"))
        coral = QColor(self.theme.color("dawn_coral"))
        gold = QColor(self.theme.color("signal_gold"))
        wood = QColor(self.theme.color("wood"))
        wood_dark = QColor(self.theme.color("wood_dark"))
        plant = QColor(self.theme.color("plant"))
        glass = self.phase_color("#BCD5D8", "#C7DCD8", "#A9BDC3", "#435C6B")
        stone = self.phase_color("#D4CDC1", "#DAD1C5", "#BDB0A3", "#252C37")
        side = stone.darker(110)
        graphite = QColor(self.theme.color("graphite"))

        # Open perimeter and a central path keep the plaza readable at a glance.
        self.addItem(IsoBlock(p, -0.3, -0.2, 17.6, 0.22, 0.58, stone.lighter(106), stone, side))
        self.addItem(IsoBlock(p, -0.3, 0.0, 0.22, 14.25, 0.58, stone.lighter(106), stone, side))
        self.addItem(IsoSurfacePatch(p, 7.15, 0.3, 2.7, 12.9, QColor("#C7C3BB") if self.phase != "night" else QColor("#2B3341"), opacity=0.52))

        portal = PortalDoor(p, 8.35, 0.32, blue)
        self.addItem(portal); self.register_animation(portal)
        self.interactions.append(InteractionSpec(
            "plaza.portal.hq", 8.35, 1.18, 1.22,
            "PORTAL", "Return to headquarters", "E  cross portal", "travel", "headquarters"
        ))

        # Signal pool with layered rim and soft center beacon.
        self.addItem(IsoBlock(p, 6.45, 5.0, 3.85, 2.5, 0.20, glass.lighter(114), glass, glass.darker(110)))
        self.addItem(IsoSurfacePatch(p, 6.82, 5.35, 3.12, 1.82, blue.lighter(172), opacity=0.42))
        beacon = BeaconItem(p, 8.35, 6.24, blue, tall=True)
        self.addItem(beacon); self.register_animation(beacon)
        self.stateful_items["plaza.fountain"] = beacon
        self.interactions.append(InteractionSpec(
            "plaza.fountain", 8.35, 7.92, 1.48,
            "SIGNAL POOL", "Wake the center of the commons", "E  toggle signal", "toggle"
        ))
        self.collisions.append(CollisionRect(6.42, 4.96, 3.92, 2.58, padding=0.05))
        self.addItem(ZoneLabel("signal pool", p.project(8.35, 8.0), QColor("#676B76")))

        # Garden pocket.
        self.addItem(IsoSurfacePatch(p, 1.15, 2.1, 4.5, 4.3, QColor("#B9C8B5") if self.phase != "night" else QColor("#27362F"), opacity=0.48))
        for x, y, s in ((1.8, 2.8, 1.12), (2.6, 3.6, 0.95), (3.7, 2.65, 1.05), (1.95, 5.0, 1.0), (4.55, 4.85, 0.95)):
            self.addItem(PlantItem(p, x, y, plant, s))
            self.collisions.append(CollisionRect(x - 0.23, y - 0.23, 0.46, 0.46, padding=0.02))
        garden_signal = BeaconItem(p, 4.45, 4.0, mint)
        self.addItem(garden_signal); self.register_animation(garden_signal)
        self.stateful_items["plaza.garden_signal"] = garden_signal
        self.interactions.append(InteractionSpec(
            "plaza.garden_signal", 4.35, 4.55, 1.18,
            "GARDEN SIGNAL", "Something is sleeping between the leaves", "E  wake signal", "beacon"
        ))
        self.addItem(ZoneLabel("garden", p.project(3.2, 6.25), QColor("#676B76")))

        # Arcade has its own silhouette instead of a colored cube.
        self.addItem(IsoBlock(p, 12.7, 2.05, 2.85, 1.55, 1.22, coral.lighter(122), coral, coral.darker(114)))
        self.addItem(IsoBlock(p, 12.95, 2.18, 2.35, 0.16, 0.24, graphite.lighter(112), graphite, graphite.darker(114), z=1.2))
        arcade_screen = ScreenItem(p, 14.1, 2.55, gold, 1.0)
        self.addItem(arcade_screen); self.register_animation(arcade_screen)
        self.stateful_items["plaza.arcade"] = arcade_screen
        self.interactions.append(InteractionSpec(
            "plaza.arcade", 13.95, 4.15, 1.42,
            "ARCADE", "The machines are warming up", "E  toggle marquee", "toggle"
        ))
        self.collisions.append(CollisionRect(12.65, 2.0, 2.95, 1.65, padding=0.04))
        self.addItem(ZoneLabel("arcade", p.project(14.1, 4.55), QColor("#676B76")))

        # Small coffee kiosk creates a second destination in the lower plaza.
        self.addItem(IsoBlock(p, 12.55, 8.15, 2.55, 1.45, 1.0, wood.lighter(116), wood, wood_dark))
        self.addItem(IsoBlock(p, 12.8, 8.35, 2.05, 0.12, 0.35, graphite.lighter(110), graphite, graphite.darker(115), z=0.55))
        self.collisions.append(CollisionRect(12.5, 8.1, 2.65, 1.55, padding=0.04))
        self.interactions.append(InteractionSpec(
            "plaza.kiosk", 12.1, 9.35, 1.30,
            "COMMONS KIOSK", "Coffee, files, and half-finished conversations", "E  inspect", "inspect"
        ))

        # Seating and lamps establish a believable public-space rhythm.
        for x, y, w, d in ((5.1, 8.9, 2.0, 0.55), (9.7, 8.9, 2.0, 0.55), (5.05, 3.35, 2.0, 0.55)):
            self.addItem(IsoBlock(p, x, y, w, d, 0.34, wood.lighter(112), wood, wood_dark))
            self.collisions.append(CollisionRect(x, y, w, d, padding=0.04))
        self.interactions.append(InteractionSpec(
            "plaza.bench", 6.05, 9.75, 1.18,
            "PLAZA BENCH", "Sit with the hum of the commons", "E  sit / stand", "sit", None,
            6.0, 9.62, 0.0, -1.0
        ))
        for x, y in ((5.7, 7.9), (11.1, 7.85), (5.25, 2.1), (11.55, 3.7)):
            lamp = FloorLampItem(p, x, y, gold)
            self.register_light(lamp)

        self.add_npc("sol", [(11.75, 10.15), (10.8, 8.9), (11.65, 7.65), (12.05, 9.0)], speed=0.38)
        mote_accent = gold if self.phase in {"dusk", "night"} else mint
        self.add_motes([(4.3,5.6,1.6),(5.1,4.9,1.3),(9.9,6.8,1.5),(11.8,6.4,1.2),(7.2,10.5,1.4),(9.0,10.7,1.2)], mote_accent)

        self.finish_build(QRectF(-1160, -390, 2320, 1520))


class RooftopScene(BaseRoomScene):
    room_id = "rooftop"
    room_label = "awake/rooftop · after-hours garden"
    width_tiles = 15
    depth_tiles = 11
    spawn = (11.9, 8.7)

    def build_world(self) -> None:
        self.reset_scene()
        self.add_floor("roof")
        p = self.projector

        blue = QColor(self.theme.color("awake_blue"))
        mint = QColor(self.theme.color("living_mint"))
        gold = QColor(self.theme.color("signal_gold"))
        lilac = QColor(self.theme.color("dream_lilac"))
        wood = QColor(self.theme.color("wood"))
        wood_dark = QColor(self.theme.color("wood_dark"))
        plant = QColor(self.theme.color("plant"))
        graphite = QColor(self.theme.color("graphite"))
        glass = self.phase_color("#BCD5D8", "#CBDDD9", "#A9BAC0", "#415A69")

        # Glass edge and low parapet imply skyline without a fake painted backdrop.
        for x in range(15):
            self.addItem(IsoBlock(p, x, -0.12, 0.96, 0.08, 0.78, glass.lighter(118), glass, glass.darker(108), opacity=0.58))
        self.addItem(IsoBlock(p, -0.25, 0.0, 0.2, 11.1, 0.52, QColor("#C8C1B5"), QColor("#AEA79C"), QColor("#9E978D")))

        # Garden strip
        self.addItem(IsoSurfacePatch(p, 1.0, 1.2, 3.8, 8.3, QColor("#9FB39B") if self.phase != "night" else QColor("#28372E"), opacity=0.42))
        for x, y, s in ((1.5, 1.9, 1.08), (2.6, 2.6, 0.95), (1.8, 4.2, 1.12), (3.4, 5.0, 1.0), (1.65, 6.8, 1.05), (3.25, 8.2, 0.92)):
            self.addItem(PlantItem(p, x, y, plant, s))
            self.collisions.append(CollisionRect(x - 0.23, y - 0.23, 0.46, 0.46, padding=0.02))

        # Pergola / listening deck
        self.addItem(IsoSurfacePatch(p, 5.1, 2.1, 5.0, 4.4, QColor("#C6B19A") if self.phase != "night" else QColor("#3A322D"), opacity=0.74))
        for x, y in ((5.3, 2.3), (9.65, 2.3), (5.3, 6.1), (9.65, 6.1)):
            self.addItem(IsoBlock(p, x, y, 0.18, 0.18, 2.2, wood.lighter(112), wood, wood_dark))
        self.addItem(IsoBlock(p, 5.25, 2.25, 4.65, 0.12, 0.12, wood.lighter(116), wood, wood_dark, z=2.12))
        self.addItem(IsoBlock(p, 5.25, 6.0, 4.65, 0.12, 0.12, wood.lighter(116), wood, wood_dark, z=2.12))

        self.addItem(IsoBlock(p, 6.3, 3.45, 2.6, 1.2, 0.20, graphite.lighter(114), graphite, graphite.darker(118), z=0.54))
        for lx, ly in ((6.45, 3.58), (8.55, 3.58), (6.45, 4.25), (8.55, 4.25)):
            self.addItem(IsoBlock(p, lx, ly, 0.16, 0.16, 0.54, graphite.lighter(108), graphite, graphite.darker(114)))
        deck_screen = ScreenItem(p, 7.55, 3.65, blue, 0.96)
        self.addItem(deck_screen); self.register_animation(deck_screen)
        self.stateful_items["roof.listening_deck"] = deck_screen
        self.interactions.append(InteractionSpec(
            "roof.listening_deck", 7.6, 5.15, 1.42,
            "LISTENING DECK", "Listen at the rooftop sound table", "E  listen / stand", "listen", "roof.listening_deck",
            7.6, 5.02, 0.0, -1.0
        ))
        self.collisions.append(CollisionRect(6.25, 3.4, 2.72, 1.34, padding=0.05))
        self.addItem(ZoneLabel("listening deck", p.project(7.6, 6.3), QColor("#676B76")))

        # Long communal table
        self.addItem(IsoBlock(p, 5.55, 7.45, 3.3, 0.9, 0.18, wood.lighter(118), wood, wood_dark, z=0.54))
        for lx, ly in ((5.75, 7.6), (8.45, 7.6)):
            self.addItem(IsoBlock(p, lx, ly, 0.18, 0.18, 0.54, graphite.lighter(108), graphite, graphite.darker(115)))
        self.collisions.append(CollisionRect(5.5, 7.4, 3.4, 1.0, padding=0.04))
        self.interactions.append(InteractionSpec(
            "roof.table", 7.1, 8.95, 1.15,
            "ROOFTOP TABLE", "Sit with something unfinished", "E  sit / stand", "sit", None,
            7.1, 8.78, 0.0, -1.0
        ))

        # Signal telescope / beacon
        beacon = BeaconItem(p, 11.2, 3.2, gold, tall=True)
        self.addItem(beacon); self.register_animation(beacon)
        self.stateful_items["roof.sky_signal"] = beacon
        self.interactions.append(InteractionSpec(
            "roof.sky_signal", 11.1, 3.75, 1.15,
            "SKY SIGNAL", "Point the network back at the horizon", "E  wake signal", "beacon"
        ))

        # Lift back down
        self.addItem(IsoBlock(p, 12.75, 7.0, 1.35, 1.55, 1.9, graphite.lighter(115), graphite, graphite.darker(118)))
        self.addItem(IsoBlock(p, 12.95, 7.18, 0.95, 0.06, 1.42, glass.lighter(118), glass, glass.darker(108), z=0.2, opacity=0.40))
        lift_door = SlidingDoorItem(p, 13.38, 7.72, blue)
        self.addItem(lift_door); self.register_animation(lift_door)
        self.transition_doors["roof.lift.hq"] = lift_door
        self.collisions.append(CollisionRect(12.7, 6.95, 1.45, 1.65, padding=0.03))
        self.interactions.append(InteractionSpec(
            "roof.lift.hq", 12.15, 8.25, 1.20,
            "LIFT", "Return to headquarters", "E  take lift", "travel", "headquarters"
        ))

        # Ambient light defines after-hours identity even during daytime.
        for x, y in ((5.1, 6.85), (10.1, 6.7), (4.75, 2.0), (10.45, 2.05)):
            lamp = FloorLampItem(p, x, y, gold)
            self.register_light(lamp)

        self.add_npc("echo", [(4.7,7.0),(4.2,5.8),(5.1,4.8),(4.5,3.6)], speed=0.34)
        sky_accent = lilac if self.phase in {"dusk", "night"} else gold
        self.add_motes([(4.8,2.7,1.4),(6.1,2.4,1.2),(8.0,2.35,1.5),(9.7,2.8,1.3),(10.9,4.5,1.6),(6.4,7.0,1.2),(8.8,7.2,1.4)], sky_accent)

        self.finish_build(QRectF(-1020, -420, 2040, 1390))



class HomeScene(BaseRoomScene):
    room_id = "home"
    room_label = "awake/home · private signal room"
    width_tiles = 13
    depth_tiles = 10
    spawn = (6.15, 8.15)

    def build_world(self) -> None:
        self.reset_scene()
        self.add_floor("home")
        p = self.projector

        blue = QColor(self.theme.color("awake_blue"))
        mint = QColor(self.theme.color("living_mint"))
        coral = QColor(self.theme.color("dawn_coral"))
        gold = QColor(self.theme.color("signal_gold"))
        wood = QColor(self.theme.color("wood"))
        wood_dark = QColor(self.theme.color("wood_dark"))
        graphite = QColor(self.theme.color("graphite"))
        plant = QColor(self.theme.color("plant"))
        glass = self.phase_color("#C9DEE1", "#D5E2DE", "#AEBCC2", "#435D6C")
        wall = self.phase_color("#EFE8DD", "#F0E4D7", "#D2C0B1", "#242B38")
        wall_side = self.phase_color("#D2C8BB", "#D7C9BA", "#B4A397", "#1A202B")

        self.addItem(IsoBlock(p, -0.3, -0.22, 13.55, 0.28, 2.52, wall, wall_side, wall_side))
        self.addItem(IsoBlock(p, -0.3, -0.02, 0.28, 10.2, 2.52, wall, wall_side, wall_side))
        self.addItem(IsoSurfacePatch(p, 4.4, 3.55, 4.0, 3.15, QColor("#B8A594") if self.phase != "night" else QColor("#35313A"), opacity=0.70))

        # Window wall and slow morning light.
        for x in (1.25, 2.5, 9.7, 10.95):
            self.addItem(IsoBlock(p, x, 0.06, 0.82, 0.055, 1.58, glass.lighter(114), glass, glass.darker(108), z=0.52, opacity=0.84))
        self.interactions.append(InteractionSpec(
            "home.window", 10.35, 1.5, 1.08,
            "WINDOW", "Watch the living network change light", "E  observe", "inspect"
        ))

        # Bed / rest pod.
        self.addItem(IsoBlock(p, 1.35, 2.15, 2.65, 1.48, 0.34, QColor("#D6C9BA"), QColor("#BFAE9E"), QColor("#A99584")))
        self.addItem(IsoBlock(p, 1.42, 2.22, 2.5, 1.31, 0.16, QColor("#F0ECE4"), QColor("#DED6CA"), QColor("#CFC5B7"), z=0.34))
        self.addItem(IsoBlock(p, 1.45, 2.18, 0.16, 1.38, 0.68, wood.lighter(114), wood, wood_dark, z=0.18))
        self.collisions.append(CollisionRect(1.3, 2.1, 2.75, 1.58, padding=0.03))
        self.interactions.append(InteractionSpec(
            "home.bed", 2.65, 4.22, 1.28,
            "REST POD", "Sleep until morning", "E  rest cycle", "sleep"
        ))

        # Personal desk / physical computer surface.
        for lx, ly in ((8.65, 2.55), (11.0, 2.55), (8.65, 3.5), (11.0, 3.5)):
            self.addItem(IsoBlock(p, lx, ly, 0.16, 0.16, 0.62, graphite.lighter(108), graphite, graphite.darker(112)))
        self.addItem(IsoBlock(p, 8.5, 2.4, 2.85, 1.32, 0.12, wood.lighter(112), wood, wood_dark, z=0.62))
        self.collisions.append(CollisionRect(8.45, 2.35, 2.95, 1.45, padding=0.04))
        desk_screen = ScreenItem(p, 9.85, 2.65, blue, 1.0)
        self.addItem(desk_screen); self.register_animation(desk_screen)
        self.stateful_items["home.desk"] = desk_screen
        self.interactions.append(InteractionSpec(
            "home.desk", 9.9, 4.35, 1.38,
            "PERSONAL DESK", "Open your private workspace", "E  sit / stand", "use", "home.desk",
            9.9, 4.18, 0.0, -1.0
        ))

        # A small shelf and listening object keep home from feeling like a menu room.
        self.addItem(ShelfItem(p, 12.0, 5.2, coral))
        self.collisions.append(CollisionRect(11.7, 4.85, 0.7, 1.05, padding=0.04))
        self.addItem(PlantItem(p, 1.25, 7.6, plant, 1.04))
        self.collisions.append(CollisionRect(1.0, 7.35, 0.5, 0.5, padding=0.02))

        # Persistent decoration anchors. E cycles only through objects already unlocked.
        anchor_specs = {
            "home.decor.a": (4.45, 4.55),
            "home.decor.b": (7.7, 4.65),
            "home.decor.c": (4.85, 7.0),
            "home.decor.d": (8.1, 7.0),
        }
        for anchor, (x, y) in anchor_specs.items():
            placed = self.state.decor.get(anchor, "")
            self.addItem(DecorAnchorItem(p, x, y, blue, occupied=bool(placed)))
            if placed:
                self.addItem(DecorItem(p, x, y, placed, blue))
            self.interactions.append(InteractionSpec(
                anchor, x, y + 0.35, 0.92,
                "DECOR ANCHOR", "Cycle placed object", "E  change decor", "decorate", anchor
            ))

        # Warm task lamp and subtle home motes.
        self.register_light(FloorLampItem(p, 7.25, 2.0, gold))
        self.add_motes([(2.2,1.3,1.3),(3.2,1.45,1.1),(9.7,1.35,1.4),(10.8,1.5,1.2),(6.4,5.5,1.0)], gold)

        # Door back into the shared world.
        door = SlidingDoorItem(p, 6.2, 0.32, blue)
        self.addItem(door); self.register_animation(door)
        self.transition_doors["home.door.hq"] = door
        self.interactions.append(InteractionSpec(
            "home.door.hq", 6.2, 1.25, 1.12,
            "THRESHOLD", "Return to headquarters", "E  open door", "travel", "headquarters"
        ))

        self.addItem(ZoneLabel("private signal room", p.project(6.5, 8.85), QColor("#676B76")))
        self.finish_build(QRectF(-930, -370, 1860, 1290))

ROOM_TYPES = {
    "headquarters": HeadquartersScene,
    "plaza": PlazaScene,
    "rooftop": RooftopScene,
    "home": HomeScene,
}


def make_room(room_id: str, theme: ThemeEngine, state: WorldState) -> BaseRoomScene:
    from awake_world.world.district import QUARTER_ROOM_TYPES
    room_cls = {**ROOM_TYPES, **QUARTER_ROOM_TYPES}.get(room_id, QUARTER_ROOM_TYPES["quarter"])
    return room_cls(theme, state)


def all_room_ids() -> set[str]:
    from awake_world.world.district import QUARTER_ROOM_TYPES
    return set(ROOM_TYPES) | set(QUARTER_ROOM_TYPES)


DISCOVERY_KEYS = {
    "hq.portal.plaza",
    "hq.project_table",
    "hq.lounge",
    "hq.media_wall",
    "hq.collab",
    "hq.lift.rooftop",
    "hq.signal",
    "hq.door.home",
    "plaza.portal.hq",
    "plaza.fountain",
    "plaza.garden_signal",
    "plaza.arcade",
    "plaza.kiosk",
    "plaza.bench",
    "roof.listening_deck",
    "roof.table",
    "roof.sky_signal",
    "roof.lift.hq",
    "home.door.hq",
    "home.desk",
    "home.bed",
    "home.window",
    "home.decor.a",
    "home.decor.b",
    "home.decor.c",
    "home.decor.d",
    "npc.mira",
    "npc.sol",
    "npc.echo",
}
