from __future__ import annotations

from dataclasses import dataclass
import hashlib


@dataclass(frozen=True, slots=True)
class ScheduleEntry:
    minute: int
    space_id: str
    action: str
    jitter: int = 0


@dataclass(frozen=True, slots=True)
class NPCRoutine:
    npc_id: str
    home: str
    job: str
    schedule: tuple[ScheduleEntry, ...]
    weather_behavior: str = "seek_shelter"
    night_behavior: str = "go_home"

    def _offset(self, day: int, entry: ScheduleEntry, seed: int) -> int:
        if entry.jitter <= 0:
            return 0
        raw = f"{seed}:{day}:{self.npc_id}:{entry.minute}:{entry.action}".encode()
        value = int(hashlib.sha256(raw).hexdigest()[:8], 16)
        return (value % (entry.jitter * 2 + 1)) - entry.jitter

    def state_at(self, minute: int, day: int = 0, seed: int = 404) -> tuple[str, str, str]:
        m = minute % 1440
        location, action = self.home, "idle"
        label = "home"
        for entry in sorted(self.schedule, key=lambda e: e.minute):
            if m >= max(0, min(1439, entry.minute + self._offset(day, entry, seed))):
                location, action, label = entry.space_id, entry.action, f"{entry.minute//60:02d}:{entry.minute%60:02d} {entry.action}"
        return location, action, label


ROUTINES = {
    "barista": NPCRoutine("barista", "offsite", "central_plaza", (
        ScheduleEntry(460,"quarter","arrive",4), ScheduleEntry(480,"central_plaza","open_cafe",2),
        ScheduleEntry(612,"central_plaza","wipe_counter",5), ScheduleEntry(750,"central_plaza","lunch",4),
        ScheduleEntry(843,"central_plaza","socialize",5), ScheduleEntry(1050,"central_plaza","clean",4),
        ScheduleEntry(1080,"offsite","leave",3),
    )),
    "courier": NPCRoutine("courier", "offsite", "quarter", (
        ScheduleEntry(540,"quarter","delivery_route",8), ScheduleEntry(660,"offsite","leave",5),
        ScheduleEntry(840,"quarter","delivery_route",8), ScheduleEntry(960,"offsite","leave",5),
    )),
    "maintenance": NPCRoutine("maintenance", "offsite", "quarter", (
        ScheduleEntry(420,"quarter","inspect",6), ScheduleEntry(720,"trinity_lab","maintenance",7),
        ScheduleEntry(900,"quarter","inspect",6), ScheduleEntry(1020,"offsite","leave",4),
    )),
    "observer": NPCRoutine("observer", "observatory", "observatory", (
        ScheduleEntry(510,"observatory","instrument_check",5), ScheduleEntry(720,"central_plaza","coffee_break",5),
        ScheduleEntry(780,"observatory","project_review",4), ScheduleEntry(1110,"observatory","horizon_observe",5),
    )),
    "operator": NPCRoutine("operator", "grid", "grid", (
        ScheduleEntry(480,"grid","systems_open",3), ScheduleEntry(660,"quarter","route_check",4),
        ScheduleEntry(720,"grid","operations",3), ScheduleEntry(1020,"grid","handoff",4),
    )),
    "developer": NPCRoutine("developer", "twin_core", "twin_core", (
        ScheduleEntry(540,"twin_core","build_review",5), ScheduleEntry(720,"central_plaza","lunch",5),
        ScheduleEntry(780,"twin_core","hardware_test",4), ScheduleEntry(1080,"twin_core","pair_session",5),
    )),
    "researcher": NPCRoutine("researcher", "trinity_lab", "trinity_lab", (
        ScheduleEntry(500,"trinity_lab","instrument_cycle",4), ScheduleEntry(690,"glasshouse","sample_check",5),
        ScheduleEntry(780,"trinity_lab","collaborate",4), ScheduleEntry(1000,"trinity_lab","archive_results",5),
    )),
    "maker": NPCRoutine("maker", "garage", "garage", (
        ScheduleEntry(500,"garage","open_bench",4), ScheduleEntry(700,"quarter","parts_run",6),
        ScheduleEntry(760,"garage","prototype",4), ScheduleEntry(1030,"garage","service_close",4),
    )),
    "host": NPCRoutine("host", "pit", "pit", (
        ScheduleEntry(780,"pit","setup_social",5), ScheduleEntry(900,"central_plaza","socialize",5),
        ScheduleEntry(1020,"pit","session_host",4), ScheduleEntry(1320,"pit","close_session",4),
    )),
    "gardener": NPCRoutine("gardener", "glasshouse", "glasshouse", (
        ScheduleEntry(450,"glasshouse","climate_check",4), ScheduleEntry(600,"kawaii_garden","watering",5),
        ScheduleEntry(780,"glasshouse","plant_care",4), ScheduleEntry(990,"kawaii_garden","garden_check",5),
    )),
}


class NPCSystem:
    def __init__(self, seed: int = 404) -> None:
        self.seed = int(seed)

    def snapshots(self, minute: int, weather: str, current_space: str, day: int = 0) -> dict[str, dict[str, object]]:
        result: dict[str, dict[str, object]] = {}
        for key, routine in ROUTINES.items():
            location, action, schedule = routine.state_at(minute, day, self.seed)
            if weather == "rain" and location in {"quarter", "central_plaza"}:
                if key == "barista":
                    action = "serve_shelter_crowd"
                elif key == "courier":
                    action = "shelter_pause"
                else:
                    action = "weather_response"
            lod = "full" if location == current_space else ("reduced" if location != "offsite" else "sleep")
            result[key] = {
                "space_id": location,
                "destination": routine.job if location != routine.job and location != "offsite" else location,
                "state": action,
                "schedule": schedule,
                "simulation_lod": lod,
                "utility_scores": {
                    "schedule": 1.0,
                    "weather": 0.85 if weather == "rain" else 0.15,
                    "player_presence": 0.35 if location == current_space else 0.0,
                },
            }
        return result

    def logical_locations(self, minute: int, weather: str) -> dict[str, str]:
        snapshots = self.snapshots(minute, weather, current_space="")
        return {key: str(value["space_id"]) for key, value in snapshots.items()}
