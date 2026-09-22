from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class SpaceType(StrEnum):
    PERSONAL = "personal_space"
    SHARED_STUDIO = "shared_studio"
    SOCIAL = "social_space"
    PUBLIC = "public_building"


@dataclass(frozen=True, slots=True)
class SpaceDefinition:
    id: str
    name: str
    owners: tuple[str, ...]
    type: SpaceType
    district: str = "awake_quarter"
    access: str = "awake_members"
    lighting_profile: str = "neutral"
    audio_profile: str = "quiet_tech"
    weather_profile: str = "standard"
    architecture_profile: str = "contemporary"
    interaction_profile: str = "contextual"
    camera_profile: str = "indoor"
    transition_profile: str = "exterior_to_interior"
    interactables: tuple[str, ...] = ()
    npc_rules: tuple[str, ...] = ()
    ambient_events: tuple[str, ...] = ()
    props: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    personalization: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PersonalSpace(SpaceDefinition):
    type: SpaceType = SpaceType.PERSONAL


@dataclass(frozen=True, slots=True)
class SharedStudio(SpaceDefinition):
    type: SpaceType = SpaceType.SHARED_STUDIO


@dataclass(frozen=True, slots=True)
class SocialSpace(SpaceDefinition):
    type: SpaceType = SpaceType.SOCIAL


@dataclass(frozen=True, slots=True)
class PublicBuilding(SpaceDefinition):
    type: SpaceType = SpaceType.PUBLIC


SPACE_CATALOG: dict[str, SpaceDefinition] = {
    "quarter": SocialSpace(
        "quarter", "Awake Quarter", (), architecture_profile="living_district", audio_profile="city_calm",
        camera_profile="outdoor", transition_profile="interior_to_exterior",
        ambient_events=("distant_pass","bird_crossing","window_light"),
    ),
    "central_plaza": SocialSpace(
        "central_plaza", "Central Plaza", (), architecture_profile="urban_garden", audio_profile="plaza",
        camera_profile="plaza", transition_profile="social",
        interactables=("cafe", "benches", "art_installation"),
        npc_rules=("barista","courier","street_musician"), ambient_events=("delivery","dog_in_plaza","street_musician"),
        props=("water","shade","urban_furniture","vegetation"),
    ),
    "observatory": PersonalSpace(
        "observatory", "The Observatory", ("caio_monks",), lighting_profile="sunset_signature",
        architecture_profile="concrete_wood_glass", audio_profile="observatory", camera_profile="indoor",
        transition_profile="exterior_to_interior", tags=("rooftop", "projects"),
        interactables=("project_wall", "main_desk", "meeting_area"), props=("smoked_glass","project_wall","rooftop_access"),
    ),
    "grid": PersonalSpace(
        "grid", "The Grid", ("bx",), lighting_profile="precise", architecture_profile="modular_geometric",
        camera_profile="indoor", transition_profile="exterior_to_interior", tags=("operations", "systems"),
    ),
    "twin_core": SharedStudio(
        "twin_core", "Twin Core", ("bruno_kuss", "vitor_kuss"), lighting_profile="graphite_tech",
        architecture_profile="game_technology_lab", audio_profile="servers", camera_profile="indoor",
        transition_profile="laboratory", tags=("dev", "hardware"), ambient_events=("server_issue","server_blink"),
        props=("dual_workstations","build_wall","servers","prototypes"),
    ),
    "trinity_lab": SharedStudio(
        "trinity_lab", "Trinity Lab", ("felipe_gomes", "fifz", "tapita"), lighting_profile="warm_research",
        architecture_profile="research_technology", camera_profile="indoor", transition_profile="laboratory",
        tags=("research", "terrace"), props=("paper_wall","experiment_room","collaboration_table","terrace"),
    ),
    "garage": PersonalSpace(
        "garage", "The Garage", ("thaynan_arruda",), lighting_profile="workshop", architecture_profile="urban_workshop",
        camera_profile="indoor", transition_profile="exterior_to_interior", tags=("prototype", "tools"),
        props=("workbench","components","boxes","large_door"),
    ),
    "kawaii_garden": PersonalSpace(
        "kawaii_garden", "Kawaii Garden", ("theus",), lighting_profile="soft_warm",
        architecture_profile="japanese_garden_tech", audio_profile="garden", weather_profile="garden_rain",
        camera_profile="social", transition_profile="garden", npc_rules=("dogs",), tags=("garden", "water"),
        ambient_events=("water_ripple","leaf_shift"), props=("water","stones","wood","pet_shelter"),
    ),
    "pit": SharedStudio(
        "pit", "The Pit", ("cabessa", "danilo_pilsen"), lighting_profile="low_chaos",
        architecture_profile="gaming_dungeon_premium", audio_profile="gaming_den", camera_profile="indoor",
        transition_profile="subterranean", tags=("gaming", "chaos"), props=("pc_wall","screens","damaged_sofa","cables"),
    ),
    "glasshouse": PersonalSpace(
        "glasshouse", "The Glasshouse", ("pure_rodrigo_valerio",), lighting_profile="bright_plant",
        architecture_profile="glass_vegetation", audio_profile="quiet_green", camera_profile="indoor",
        transition_profile="garden", tags=("minimal", "plants"), props=("glass","vegetation","diffused_fabric"),
    ),
}


class SpaceSystem:
    def __init__(self, state, catalog: dict[str, SpaceDefinition] | None = None) -> None:
        self.state = state
        self.catalog = catalog or SPACE_CATALOG
        self.current_space = state.last_room if state.last_room in self.catalog else "quarter"

    def get(self, space_id: str) -> SpaceDefinition:
        return self.catalog[space_id]

    def exists(self, space_id: str) -> bool:
        return space_id in self.catalog

    def enter(self, space_id: str) -> SpaceDefinition:
        definition = self.get(space_id)
        self.current_space = space_id
        self.state.last_room = space_id
        state = self.state.space_states.setdefault(space_id, {})
        state["visits"] = int(state.get("visits", 0)) + 1
        state["lighting_profile"] = definition.lighting_profile
        state["audio_profile"] = definition.audio_profile
        return definition


def get_space(space_id: str) -> SpaceDefinition:
    return SPACE_CATALOG[space_id]
