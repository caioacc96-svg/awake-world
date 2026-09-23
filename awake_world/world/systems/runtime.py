from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from awake_world.world.systems.ambient_life import AmbientLifeSystem
from awake_world.world.systems.audio_zones import AudioZone, AudioZoneSystem
from awake_world.world.systems.diagnostics import DiagnosticsSystem
from awake_world.world.systems.events import EventBus, WorldEvent
from awake_world.world.systems.hardening import HardeningSystem
from awake_world.world.systems.interactions import InteractionSystem
from awake_world.world.systems.lighting_system import LightingSystem
from awake_world.world.systems.microevents import MicroEventSystem
from awake_world.world.systems.npc_system import NPCSystem
from awake_world.world.systems.pets import PetSystem
from awake_world.world.systems.performance import PerformanceSystem
from awake_world.world.systems.presence import PresenceMode, PresenceSystem
from awake_world.world.systems.spaces import SpaceSystem
from awake_world.world.systems.surfaces import SurfaceOccupancySystem
from awake_world.world.systems.time_system import TimeSystem
from awake_world.world.systems.weather import WeatherSystem


@dataclass(slots=True)
class RuntimeMetrics:
    simulation_tick: int = 0
    simulation_steps_last_frame: int = 0
    simulation_time_ms: float = 0.0
    active_npcs: int = 0
    sleeping_actors: int = 0
    active_lights: int = 0
    audio_sources: int = 0
    scene_objects: int = 0
    simulation_lod: str = "full"
    hardening_fallbacks: int = 0


class WorldRuntime:
    """Deterministic single-player backbone with explicit presentation/network boundaries."""

    FIXED_HZ = 60

    def __init__(self, state, minutes_per_real_second: float = 0.5) -> None:
        self.state = state
        self.bus = EventBus()
        self.time = TimeSystem(self.bus, state, minutes_per_real_second)
        self.weather = WeatherSystem(self.bus, state.weather, state.weather_intensity, seed=state.world_seed)
        self.presence = PresenceSystem(self.bus, state.presence)
        self.microevents = MicroEventSystem(self.bus, state.active_events, seed=state.world_seed)
        self.npcs = NPCSystem(state.world_seed)
        self.pets = PetSystem(state.world_seed)
        self.ambient = AmbientLifeSystem(state.world_seed)
        self.spaces = SpaceSystem(state)
        self.surfaces = SurfaceOccupancySystem(state)
        self.audio_zones = AudioZoneSystem()
        self.lighting = LightingSystem()
        self.interactions = InteractionSystem()
        self.performance = PerformanceSystem()
        self.hardening = HardeningSystem()
        self.diagnostics = DiagnosticsSystem()
        self.metrics = RuntimeMetrics()
        self.current_space = self.spaces.current_space
        self._accumulator = 0.0
        self._day = 0
        self.paused = False
        self.simulation_speed = 1.0
        self.state.pet_states = self.pets.tick(0.0, self.state.weather, int(self.time.minutes), self.current_space)
        self._sync_derived_state(update_npcs=True)

    @property
    def fixed_dt(self) -> float:
        return 1.0 / self.FIXED_HZ

    def enter_space(self, space_id: str) -> None:
        old = self.current_space
        if old != space_id:
            self.bus.publish(WorldEvent.PLAYER_LEFT_SPACE, space_id=old)
        self.current_space = space_id
        if self.spaces.exists(space_id):
            definition = self.spaces.enter(space_id)
            indoor = space_id not in {"quarter", "central_plaza", "kawaii_garden"}
            rain_surface = (
                "glass" if space_id in {"observatory", "glasshouse"}
                else "metal" if space_id in {"garage", "twin_core"}
                else "vegetation" if space_id == "kawaii_garden"
                else "concrete" if space_id == "central_plaza"
                else "roof"
            )
            self.audio_zones.enter(AudioZone(space_id, definition.audio_profile, indoor=indoor, rain_surface=rain_surface))
        else:
            self.state.last_room = space_id
            self.audio_zones.enter(AudioZone(space_id, "legacy_room", indoor=True, rain_surface="roof"))
        self.interactions.clear()
        self.presence.set("local_player", space_id, PresenceMode.AVAILABLE)
        self.bus.publish(WorldEvent.PLAYER_ENTERED_SPACE, space_id=space_id)
        self.diagnostics.event("SPACE", action="enter", space_id=space_id)
        self._sync_derived_state(update_npcs=True)

    def set_weather(self, kind: str) -> None:
        self.weather.set(kind)
        self.diagnostics.event("WEATHER", weather=kind)
        self._sync_derived_state(update_npcs=True)

    def set_speed(self, speed: float) -> None:
        self.simulation_speed = max(0.0, min(4.0, float(speed)))

    def set_paused(self, paused: bool) -> None:
        self.paused = bool(paused)

    def single_tick(self) -> dict[str, Any]:
        minute_changed, phase_changed = self._fixed_tick(self.fixed_dt)
        return {"steps": 1, "minute_changed": minute_changed, "phase_changed": phase_changed}

    def tick(self, dt: float) -> dict[str, Any]:
        if self.paused:
            self.metrics.simulation_steps_last_frame = 0
            return {"steps": 0, "minute_changed": False, "phase_changed": False}
        frame_dt = self.hardening.clamp_frame_dt(dt)
        self.metrics.hardening_fallbacks = self.hardening.fallback_count
        budget = self.hardening.budget
        self._accumulator = min(
            self._accumulator + frame_dt * self.simulation_speed,
            budget.max_accumulator,
        )
        steps = 0
        minute_changed = False
        phase_changed = False
        while self._accumulator + 1e-12 >= self.fixed_dt:
            m, p = self._fixed_tick(self.fixed_dt)
            minute_changed = minute_changed or m
            phase_changed = phase_changed or p
            self._accumulator -= self.fixed_dt
            steps += 1
        self.metrics.simulation_steps_last_frame = steps
        return {"steps": steps, "minute_changed": minute_changed, "phase_changed": phase_changed}

    def _fixed_tick(self, dt: float) -> tuple[bool, bool]:
        minute_changed, phase_changed = self.time.advance(dt)
        self.weather.tick(dt)
        self.microevents.tick(dt, self.current_space)
        self.audio_zones.tick(dt)

        next_tick = self.metrics.simulation_tick + 1
        budget = self.hardening.budget
        if self.hardening.due(next_tick, budget.ambient_divisor):
            ambient_dt = dt * budget.ambient_divisor
            for ambient in self.ambient.tick(ambient_dt, self.current_space, self.state.weather, int(self.time.minutes)):
                self.bus.publish(
                    WorldEvent.AMBIENT_EVENT,
                    key=ambient.key,
                    category=ambient.category,
                    space_id=ambient.space_id,
                    strength=ambient.strength,
                )
        if self.hardening.due(next_tick, budget.pet_divisor):
            self.state.pet_states = self.pets.tick(
                dt * budget.pet_divisor,
                self.state.weather,
                int(self.time.minutes),
                self.current_space,
            )

        self.metrics.simulation_tick = next_tick
        self._sync_derived_state(
            update_npcs=self.hardening.due(next_tick, budget.npc_sync_divisor)
        )
        return minute_changed, phase_changed

    def _sync_derived_state(self, update_npcs: bool = True) -> None:
        self.state.weather = self.weather.state.kind.value
        self.state.weather_intensity = self.weather.state.intensity
        self.state.active_events = self.microevents.snapshot()
        self.state.presence = self.presence.snapshot()
        if update_npcs or not self.state.npc_states:
            self.state.npc_states = self.npcs.snapshots(
                int(self.time.minutes),
                self.state.weather,
                self.current_space,
                self._day,
            )
        self.state.environment_state = {
            "phase": self.time.phase,
            "audio_mix": self.audio_mix(),
            "lighting_exposure": self.resolved_lighting().global_exposure,
            "ambient_life": self.ambient.snapshot(),
            "surface_occupancy": self.surfaces.snapshot(self.current_space),
            "hardening_fallbacks": self.hardening.fallback_count,
        }
        self.metrics.active_npcs = sum(
            1 for value in self.state.npc_states.values()
            if value.get("simulation_lod") in {"full", "reduced"}
        )
        self.metrics.sleeping_actors = sum(
            1 for value in self.state.npc_states.values()
            if value.get("simulation_lod") == "sleep"
        )

    def resolved_lighting(self):
        return self.lighting.resolve(self.time.phase, self.state.weather)

    def audio_mix(self) -> dict[str, float]:
        return self.audio_zones.mix(self.state.weather)

    def snapshot(self) -> dict[str, Any]:
        return {
            "time": round(self.time.minutes, 3),
            "phase": self.time.phase,
            "weather": self.state.weather,
            "seed": self.state.world_seed,
            "tick": self.metrics.simulation_tick,
            "space": self.current_space,
            "active_events": sorted(self.microevents.active),
            "npc_states": self.state.npc_states,
            "pet_states": self.state.pet_states,
            "audio_mix": self.audio_mix(),
            "surface_occupancy": self.surfaces.snapshot(self.current_space),
            "hardening_fallbacks": self.hardening.fallback_count,
        }
