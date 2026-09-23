from __future__ import annotations

import math
import time
from dataclasses import replace

from PySide6.QtCore import QPointF, Qt, QTimer, Signal
from PySide6.QtGui import QKeyEvent, QPainter, QWheelEvent
from PySide6.QtWidgets import QFrame, QGraphicsView

from awake_world import __version__
from awake_world.design.theme.engine import ThemeEngine
from awake_world.world.audio import AudioManager
from awake_world.world.items import InteractionSpec
from awake_world.world.lighting import format_world_time
from awake_world.world.progression import evaluate_progression, inventory_lines, journal_lines
from awake_world.world.room import DISCOVERY_KEYS, BaseRoomScene, all_room_ids, make_room
from awake_world.world.systems import WorldEvent, WorldRuntime
from awake_world.world.systems.spaces import SPACE_CATALOG
from awake_world.simulation import ActorRuntime, MovementConfig, SimulationRecorder, Vec2
from awake_world.presentation import CAMERA_PROFILES, CameraController, SpaceTransitionOrchestrator
from awake_world.presentation.transition_orchestrator import PROFILES
from awake_world.world.save import load_state, save_state, state_payload


class GameView(QGraphicsView):
    interactionChanged = Signal(object)
    worldMessage = Signal(str)
    roomChanged = Signal(str)
    explorationChanged = Signal(int, int)
    timeChanged = Signal(str, str)
    snapshotChanged = Signal(object)
    panelRequested = Signal(str)

    def __init__(self, theme: ThemeEngine, parent=None) -> None:
        self.state = load_state()
        self.state.build_version = __version__
        self.theme = theme
        self.runtime = WorldRuntime(
            self.state,
            minutes_per_real_second=float(theme.value("world_minutes_per_real_second", 0.5)),
        )
        self.clock = self.runtime.time
        valid_rooms = all_room_ids()
        self.room_id = self.state.last_room if self.state.last_room in valid_rooms else "quarter"
        self.world: BaseRoomScene = make_room(self.room_id, theme, self.state)
        self.world.apply_weather(self.state.weather)
        saved_player = self.state.player_state if isinstance(self.state.player_state, dict) else {}
        if str(saved_player.get("space_id", "")) == self.room_id:
            position = saved_player.get("position")
            if isinstance(position, (list, tuple)) and len(position) >= 2:
                try:
                    px, py = float(position[0]), float(position[1])
                    if self.world.can_move_to(px, py):
                        self.world.avatar.grid_x = px
                        self.world.avatar.grid_y = py
                        self.world.avatar.grid_z = self.world.elevation_at(px, py)
                        self.world.avatar.sync_scene_position()
                except (TypeError, ValueError):
                    pass
        walk_speed = float(theme.value("avatar_speed_tiles_s", 3.35))
        run_speed = walk_speed * float(theme.value("avatar_sprint_multiplier", 1.45))
        self.actor_runtime = ActorRuntime(
            "local_player",
            position=Vec2(self.world.avatar.grid_x, self.world.avatar.grid_y),
            config=MovementConfig(walk_speed=walk_speed, run_speed=run_speed, fixed_hz=60),
        )
        saved_facing = saved_player.get("facing")
        if isinstance(saved_facing, (list, tuple)) and len(saved_facing) >= 2:
            try:
                self.actor_runtime.facing = Vec2(float(saved_facing[0]), float(saved_facing[1])).normalized()
            except (TypeError, ValueError):
                pass
        self.camera_controller = CameraController()
        self.transition = SpaceTransitionOrchestrator()
        self.recorder = SimulationRecorder(self.state.world_seed)
        self._pending_room_id: str | None = None
        self._user_zoom = 1.0
        super().__init__(self.world, parent)

        self.audio = AudioManager()
        self.keys: set[int] = set()
        self._last_time = time.perf_counter()
        self._last_interaction: InteractionSpec | None = None
        self._last_autosave = self._last_time
        self._transitioning = False
        self.runtime.bus.subscribe(WorldEvent.WEATHER_CHANGED, self._on_runtime_weather)
        self.runtime.bus.subscribe(WorldEvent.MICROEVENT_STARTED, self._on_microevent_started)
        self.runtime.enter_space(self.room_id)

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.scale(1.02, 1.02)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)
        QTimer.singleShot(0, self._announce_state)

    def _announce_state(self) -> None:
        self.roomChanged.emit(self.world.room_label)
        self.explorationChanged.emit(len(self.state.discovered & DISCOVERY_KEYS), len(DISCOVERY_KEYS))
        self.timeChanged.emit(format_world_time(self.clock.minutes), self.clock.phase)
        self._snap_camera()
        self._apply_ambient_audio()
        self._evaluate_progression()
        self._emit_snapshot()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if event.oldSize().width() <= 0:
            self._snap_camera()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key.Key_E and not event.isAutoRepeat():
            self.interact_current()
            event.accept()
            return
        if key == Qt.Key.Key_T and not event.isAutoRepeat():
            self.cycle_time_phase()
            event.accept()
            return
        if key == Qt.Key.Key_F3 and not event.isAutoRepeat():
            self.panelRequested.emit("world_debug")
            event.accept()
            return
        if key == Qt.Key.Key_I and not event.isAutoRepeat():
            self.panelRequested.emit("field_notes")
            event.accept()
            return
        if key in (
            Qt.Key.Key_W, Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D,
            Qt.Key.Key_Up, Qt.Key.Key_Left, Qt.Key.Key_Down, Qt.Key.Key_Right,
            Qt.Key.Key_Shift,
        ):
            self.keys.add(key)
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if not event.isAutoRepeat():
            self.keys.discard(event.key())
        super().keyReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        factor = 1.10 if event.angleDelta().y() > 0 else 1 / 1.10
        target = self._user_zoom * factor
        if 0.72 <= target <= 1.55:
            self._user_zoom = target

    def cycle_time_phase(self) -> None:
        target = self.clock.cycle_phase()
        self.state.world_minutes = self.clock.minutes
        self.world.set_world_time(self.clock.minutes, force=True)
        self._snap_camera()
        self.timeChanged.emit(format_world_time(self.clock.minutes), target)
        self.worldMessage.emit(f"World light · {target}")
        self._apply_ambient_audio()
        self._evaluate_progression()
        save_state(self.state)
        self._emit_snapshot()
        self._refresh_interaction(force=True)

    def interact_current(self) -> None:
        if self._transitioning:
            return
        current = self.world.closest_interaction()
        if not current:
            if self.world.avatar.locked_in_pose:
                self.world.release_local_surface()
                self.world.avatar.stand()
                self.worldMessage.emit("Back on your feet")
            return

        outcome = self.world.activate(current)
        if self.world.avatar.locked_in_pose:
            self.actor_runtime.teleport(self.world.avatar.grid_x, self.world.avatar.grid_y)
        if outcome.set_time is not None:
            self.clock.minutes = float(outcome.set_time) % (24 * 60)
            self.state.world_minutes = self.clock.minutes
            self.world.set_world_time(self.clock.minutes, force=True)
            self.timeChanged.emit(format_world_time(self.clock.minutes), self.clock.phase)
            self._apply_ambient_audio()

        if outcome.rebuild:
            self.world.rebuild_preserving_avatar()
            self._snap_camera()

        self.audio.play_fx("discover" if outcome.discovery else "interact")
        self.worldMessage.emit(outcome.message)
        self.explorationChanged.emit(len(self.state.discovered & DISCOVERY_KEYS), len(DISCOVERY_KEYS))
        self._evaluate_progression()
        save_state(self.state)
        self._emit_snapshot()

        if outcome.travel_to:
            self._start_travel(outcome.travel_to)
        else:
            self._refresh_interaction(force=True)

    def _transition_profile_for(self, source: str, target: str) -> str:
        if target == "quarter" and source not in {"quarter", "central_plaza"}:
            return "interior_to_exterior"
        definition = SPACE_CATALOG.get(target)
        if definition is not None:
            return definition.transition_profile
        if target == "rooftop":
            return "rooftop"
        return "exterior_to_interior"

    def _start_travel(self, room_id: str) -> None:
        self._transitioning = True
        self._pending_room_id = room_id
        self.keys.clear()
        self.actor_runtime.clear_input()
        self.world.release_local_surface()
        self.world.avatar.stand()
        profile = self._transition_profile_for(self.room_id, room_id)
        transition_state = self.transition.start(self.room_id, room_id, profile)
        duration = PROFILES[transition_state.profile].total_ms / 1000.0
        self.audio.crossfade_to(self._ambient_name_for(room_id), duration * PROFILES[transition_state.profile].audio_crossfade)
        self.runtime.bus.publish(WorldEvent.TRANSITION_STARTED, source=self.room_id, target=room_id, profile=profile)

    def _switch_room(self, room_id: str, transition_handoff: bool = False) -> None:
        self.world.release_local_surface()
        self.state.world_minutes = self.clock.minutes
        self.room_id = room_id
        self.state.last_room = room_id
        self.world = make_room(room_id, self.theme, self.state)
        self.world.set_world_time(self.clock.minutes, force=False)
        self.world.apply_weather(self.runtime.weather.state.kind.value)
        self.runtime.enter_space(room_id)
        self.setScene(self.world)
        self.keys.clear()
        self._last_interaction = None
        self.actor_runtime.teleport(self.world.avatar.grid_x, self.world.avatar.grid_y)
        if not transition_handoff:
            self._transitioning = False
            self._pending_room_id = None
        save_state(self.state)
        self._snap_camera()
        self.roomChanged.emit(self.world.room_label)
        self.interactionChanged.emit(None)
        if not transition_handoff:
            self._apply_ambient_audio()
        self._evaluate_progression()
        self._emit_snapshot()

    def _ambient_name_for(self, room_id: str) -> str:
        suffix = "night" if self.clock.phase in {"dusk", "night"} else "day"
        prefix = {"headquarters": "hq", "quarter": "plaza", "central_plaza": "plaza"}.get(room_id, room_id)
        candidate = f"{prefix}_{suffix}"
        known = {"hq_day","hq_night","plaza_day","plaza_night","rooftop_day","rooftop_night","home_day","home_night"}
        return candidate if candidate in known else f"hq_{suffix}"

    def _ambient_name(self) -> str:
        return self._ambient_name_for(self.room_id)

    def _apply_ambient_audio(self) -> None:
        self.audio.set_ambient(self._ambient_name())

    def _evaluate_progression(self) -> None:
        messages = evaluate_progression(self.state, self.room_id, self.clock.phase)
        if messages:
            self.audio.play_fx("discover")
            self.worldMessage.emit(messages[-1])
            save_state(self.state)
            self._emit_snapshot()

    def _emit_snapshot(self) -> None:
        self.snapshotChanged.emit({
            "inventory": inventory_lines(self.state),
            "journal": journal_lines(self.state),
            "flags": sorted(self.state.flags),
            "room": self.room_id,
            "visits": dict(self.state.visits),
            "discoveries": len(self.state.discovered & DISCOVERY_KEYS),
            "discovery_total": len(DISCOVERY_KEYS),
            "audio": self.audio.available,
            "weather": self.runtime.weather.state.kind.value,
            "weather_intensity": self.runtime.weather.state.intensity,
            "active_events": sorted(self.runtime.microevents.active),
            "active_npcs": len(self.world.npcs),
            "active_lights": len(self.world.ambient_lights),
            "audio_mix": self.runtime.audio_mix(),
            "lighting": self.runtime.resolved_lighting().global_exposure,
            "player": self.actor_runtime.snapshot(),
            "simulation_tick": self.runtime.metrics.simulation_tick,
            "simulation_steps": self.runtime.metrics.simulation_steps_last_frame,
            "simulation_paused": self.runtime.paused,
            "simulation_speed": self.runtime.simulation_speed,
            "hardening_fallbacks": self.runtime.metrics.hardening_fallbacks,
            "elevation": round(self.world.avatar.grid_z, 4),
            "surface_occupancy": self.runtime.surfaces.snapshot(self.room_id),
            "camera": {"x": round(self.camera_controller.state.x,2), "y": round(self.camera_controller.state.y,2), "zoom": round(self.camera_controller.state.zoom,3)},
            "pet_states": dict(self.state.pet_states),
            "npc_states": dict(self.state.npc_states),
        })

    def _on_runtime_weather(self, event) -> None:
        weather = str(event.payload.get("weather", "clear"))
        self.world.apply_weather(weather)
        self.worldMessage.emit(f"Weather · {weather}")
        self._emit_snapshot()

    def _on_microevent_started(self, event) -> None:
        key = str(event.payload.get("key", "event"))
        labels = {
            "delivery": "A delivery crossed the quarter",
            "courier_arrival": "Courier route · a package changed hands",
            "maintenance_pass": "Maintenance · a quiet inspection passed nearby",
            "cafe_cycle": "Commons café · service rhythm changed",
            "garden_watering": "Garden irrigation · short cycle",
            "instrument_cycle": "Observatory · instrument cycle complete",
            "system_check": "Grid · operational check complete",
            "build_cycle": "Twin Core · build state refreshed",
            "research_cycle": "Trinity Lab · instrument cycle complete",
            "service_cycle": "Garage · service bench changed state",
            "pet_pause": "Kawaii Garden · Momo settled nearby",
            "social_gathering": "A small social cluster formed",
            "climate_cycle": "Glasshouse · climate system adjusted",
            "dog_in_plaza": "A dog wandered into Central Plaza",
            "rooftop_session": "A distant rooftop session started",
            "power_flicker": "Power flicker · local systems recovered",
            "server_issue": "Twin Core reports unusual server activity",
            "street_musician": "Music drifts through the district",
        }
        self.worldMessage.emit(labels.get(key, f"Microevent · {key}"))
        self._emit_snapshot()

    def set_weather(self, weather: str) -> None:
        self.runtime.set_weather(weather)
        save_state(self.state)

    def jump_to_time(self, minutes: float) -> None:
        self.clock.minutes = float(minutes) % (24 * 60)
        self.state.world_minutes = self.clock.minutes
        self.world.set_world_time(self.clock.minutes, force=True)
        self.world.apply_weather(self.runtime.weather.state.kind.value)
        self.timeChanged.emit(format_world_time(self.clock.minutes), self.clock.phase)
        self._apply_ambient_audio()
        save_state(self.state)

    def teleport(self, room_id: str) -> None:
        if room_id in all_room_ids() and not self._transitioning:
            self._switch_room(room_id)

    def trigger_microevent(self, key: str) -> None:
        self.runtime.microevents.trigger(key, self.room_id)
        save_state(self.state)

    def set_simulation_speed(self, speed: float) -> None:
        self.runtime.set_speed(speed)
        self.worldMessage.emit(f"Simulation · {speed:g}x")
        self._emit_snapshot()

    def toggle_simulation_pause(self) -> None:
        self.runtime.set_paused(not self.runtime.paused)
        self.worldMessage.emit("Simulation · paused" if self.runtime.paused else "Simulation · running")
        self._emit_snapshot()

    def single_simulation_tick(self) -> None:
        was_paused = self.runtime.paused
        self.runtime.set_paused(True)
        result = self.runtime.single_tick()
        self.runtime.set_paused(was_paused or True)
        if result.get("phase_changed"):
            self.world.set_world_time(self.clock.minutes, force=True)
            self.actor_runtime.teleport(self.world.avatar.grid_x, self.world.avatar.grid_y)
            self._snap_camera()
        self._emit_snapshot()

    def export_diagnostics(self) -> str:
        self._sync_player_state()
        performance = {
            "simulation_tick": self.runtime.metrics.simulation_tick,
            "simulation_steps_last_frame": self.runtime.metrics.simulation_steps_last_frame,
            "active_npcs": self.runtime.metrics.active_npcs,
            "sleeping_actors": self.runtime.metrics.sleeping_actors,
            "active_lights": len(self.world.ambient_lights),
            "scene_objects": len(self.world.items()),
            "audio_sources": len([v for v in self.runtime.audio_mix().values() if v > 0.01]),
        }
        path = self.runtime.diagnostics.export(
            {"build_version": self.state.build_version, "save_schema": self.state.schema_version, "identity": "awake/world — THE LIVING NETWORK"},
            state_payload(self.state),
            performance,
            replay=self.recorder.to_dict(),
        )
        self.worldMessage.emit(f"Diagnostics exported · {path.name}")
        return str(path)

    def _tick(self) -> None:
        now = time.perf_counter()
        dt = min(now - self._last_time, 0.05)
        self._last_time = now
        runtime_step = self.runtime.tick(dt)
        minute_changed = bool(runtime_step.get("minute_changed"))
        phase_changed = bool(runtime_step.get("phase_changed"))
        if minute_changed:
            self.state.world_minutes = self.clock.minutes
            self.timeChanged.emit(format_world_time(self.clock.minutes), self.clock.phase)
        if phase_changed:
            self.world.set_world_time(self.clock.minutes, force=True)
            self.actor_runtime.teleport(self.world.avatar.grid_x, self.world.avatar.grid_y)
            self._snap_camera()
            self._apply_ambient_audio()
            self._evaluate_progression()
            self._refresh_interaction(force=True)

        if now - self._last_autosave >= 12.0:
            self._sync_player_state()
            save_state(self.state)
            self._last_autosave = now

        if self.transition.active:
            transition_state = self.transition.tick(dt)
            if transition_state.handoff_ready and self._pending_room_id:
                target = self._pending_room_id
                self._switch_room(target, transition_handoff=True)
            if transition_state.complete:
                self._transitioning = False
                self._pending_room_id = None
                self.runtime.bus.publish(WorldEvent.TRANSITION_COMPLETED, space_id=self.room_id)

        dx = 0.0; dy = 0.0
        if Qt.Key.Key_W in self.keys or Qt.Key.Key_Up in self.keys: dy -= 1.0
        if Qt.Key.Key_S in self.keys or Qt.Key.Key_Down in self.keys: dy += 1.0
        if Qt.Key.Key_A in self.keys or Qt.Key.Key_Left in self.keys: dx -= 1.0
        if Qt.Key.Key_D in self.keys or Qt.Key.Key_Right in self.keys: dx += 1.0

        avatar = self.world.avatar
        sprinting = Qt.Key.Key_Shift in self.keys
        movement_locked = self._transitioning and self.transition.snapshot.movement_locked
        moving_input = bool(dx or dy) and not movement_locked
        if moving_input and avatar.locked_in_pose:
            self.world.release_local_surface()
            avatar.stand()
            self.actor_runtime.teleport(avatar.grid_x, avatar.grid_y)

        if avatar.locked_in_pose or movement_locked:
            self.actor_runtime.clear_input()
        else:
            self.actor_runtime.set_input(dx, dy, sprinting)
        self.actor_runtime.advance(dt, self.world.can_move_to)
        visual = self.actor_runtime.interpolated_position()
        avatar.grid_x = visual.x
        avatar.grid_y = visual.y
        avatar.grid_z = self.world.elevation_at(visual.x, visual.y)
        velocity = self.actor_runtime.velocity
        if velocity.length() > 0.01:
            avatar.set_facing(velocity.x, velocity.y)
        avatar.set_motion_state(velocity.length() > 0.03, self.actor_runtime.state.value == "run")
        avatar.sync_scene_position()

        self.audio.tick(dt)
        self._smooth_camera(dt)
        avatar.advance_animation(dt)
        self._apply_actor_presentation_states()
        self.world.advance_ambient(dt)
        self._sync_player_state()
        input_state = {"dx": round(self.actor_runtime.input_direction.x, 4), "dy": round(self.actor_runtime.input_direction.y, 4), "run": self.actor_runtime.running}
        self.runtime.diagnostics.input(tick=self.runtime.metrics.simulation_tick, **input_state)
        recent_events = [{"kind": e.kind.value, "payload": e.payload} for e in list(self.runtime.bus.recent)[-4:]]
        self.recorder.record(
            self.runtime.metrics.simulation_tick,
            input_state,
            {"local_player": self.actor_runtime.snapshot()},
            recent_events,
            [{"phase": self.transition.snapshot.phase.value, "progress": round(self.transition.snapshot.progress, 4)}] if self.transition.active else [],
        )
        self._refresh_interaction()

    def _apply_actor_presentation_states(self) -> None:
        for key, item in self.world.npcs.items():
            if key == "momo":
                snapshot = self.state.pet_states.get(key, {})
            else:
                snapshot = self.state.npc_states.get(key, {})
            logical_space = str(snapshot.get("space_id", self.room_id)) if isinstance(snapshot, dict) else self.room_id
            item.setVisible(logical_space == self.room_id)
            if isinstance(snapshot, dict):
                item.set_behavior_state(str(snapshot.get("state", "idle")))

    def _camera_profile(self):
        definition = SPACE_CATALOG.get(self.room_id)
        key = definition.camera_profile if definition is not None else ("rooftop" if self.room_id == "rooftop" else "indoor")
        base = CAMERA_PROFILES.get(key, CAMERA_PROFILES["indoor"])
        zoom = base.zoom * self._user_zoom
        if self.transition.active:
            profile = PROFILES[self.transition.snapshot.profile]
            q = self.transition.snapshot.progress
            transition_curve = math.sin(math.pi * max(0.0, min(1.0, q)))
            zoom *= 1.0 + profile.camera_zoom_delta * transition_curve
        return replace(base, zoom=zoom)

    def _snap_camera(self) -> None:
        target = self.world.avatar.scenePos()
        profile = self._camera_profile()
        state = self.camera_controller.snap(target.x(), target.y(), profile.zoom)
        self.centerOn(QPointF(state.x, state.y))
        current = self.transform().m11()
        if current > 0.001:
            factor = state.zoom / current
            self.scale(factor, factor)

    def _smooth_camera(self, dt: float) -> None:
        avatar = self.world.avatar
        target = avatar.scenePos()
        vx, vy = self.actor_runtime.velocity.x, self.actor_runtime.velocity.y
        p0 = self.world.projector.project(avatar.grid_x, avatar.grid_y, avatar.grid_z)
        p1 = self.world.projector.project(
            avatar.grid_x + vx,
            avatar.grid_y + vy,
            self.world.elevation_at(avatar.grid_x + vx, avatar.grid_y + vy),
        )
        state = self.camera_controller.update(
            dt, target.x(), target.y(), p1.x()-p0.x(), p1.y()-p0.y(), self._camera_profile()
        )
        self.centerOn(QPointF(state.x, state.y))
        current = self.transform().m11()
        if current > 0.001 and abs(state.zoom-current) > 0.0005:
            factor = state.zoom / current
            self.scale(factor, factor)

    def _sync_player_state(self) -> None:
        self.state.player_state = {
            "space_id": self.room_id,
            "position": [round(self.actor_runtime.position.x, 4), round(self.actor_runtime.position.y, 4)],
            "elevation": round(self.world.avatar.grid_z, 4),
            "velocity": [round(self.actor_runtime.velocity.x, 4), round(self.actor_runtime.velocity.y, 4)],
            "state": self.actor_runtime.state.value,
            "facing": [round(self.actor_runtime.facing.x, 4), round(self.actor_runtime.facing.y, 4)],
        }

    def _refresh_interaction(self, force: bool = False) -> None:
        current = self.world.closest_interaction()
        if force or current != self._last_interaction:
            self._last_interaction = current
            self.interactionChanged.emit(current)
