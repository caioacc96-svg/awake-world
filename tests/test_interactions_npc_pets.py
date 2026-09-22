from dataclasses import dataclass
from awake_world.world.systems.interactions import InteractionSystem
from awake_world.world.systems.npc_system import NPCSystem
from awake_world.world.systems.pets import PetSystem

@dataclass(frozen=True)
class I:
    x: float; y: float; radius: float; key: str


def test_interaction_hysteresis():
    a=I(0,0,2,"a"); b=I(.05,0,2,"b")
    system=InteractionSystem(switch_margin=.2)
    first=system.nearest([a,b],0,0,None)
    second=system.nearest([a,b],.03,0,None)
    assert first is a and second is a


def test_npc_weather_changes_action():
    n=NPCSystem(404)
    s=n.snapshots(9*60,"rain","quarter")
    assert s["courier"]["state"] in {"shelter_pause","delivery_route","leave"}
    assert "utility_scores" in s["barista"]


def test_pet_seeks_shelter_in_rain_eventually():
    p=PetSystem(404)
    state=None
    for _ in range(20):
        state=p.tick(1.0,"rain",12*60,"kawaii_garden")["momo"]["state"]
        if state == "seek_shelter": break
    assert state == "seek_shelter"
