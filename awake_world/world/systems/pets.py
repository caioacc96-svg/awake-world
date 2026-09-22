from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import random


class PetState(StrEnum):
    IDLE = "idle"
    WANDER = "wander"
    SNIFF = "sniff"
    OBSERVE = "observe"
    FOLLOW = "follow"
    SIT = "sit"
    PLAY = "play"
    EAT = "eat"
    SLEEP = "sleep"
    SEEK_SHELTER = "seek_shelter"


@dataclass(slots=True)
class PetSnapshot:
    pet_id: str
    space_id: str
    state: PetState = PetState.IDLE
    action_age: float = 0.0


class PetSystem:
    def __init__(self, seed: int = 404) -> None:
        self._rng = random.Random(seed + 91)
        self.pets = {"momo": PetSnapshot("momo", "kawaii_garden")}

    def _utilities(self, pet: PetSnapshot, weather: str, minute: int, player_space: str) -> dict[PetState, float]:
        night = minute % 1440 >= 21 * 60 or minute % 1440 < 6 * 60
        nearby = player_space == pet.space_id
        u = {
            PetState.IDLE: 0.36, PetState.WANDER: 0.30, PetState.SNIFF: 0.28,
            PetState.OBSERVE: 0.26 + (0.25 if nearby else 0.0),
            PetState.FOLLOW: 0.12 + (0.22 if nearby else 0.0),
            PetState.SIT: 0.27, PetState.PLAY: 0.16 + (0.12 if nearby else 0.0),
            PetState.EAT: 0.10, PetState.SLEEP: 0.18 + (0.62 if night else 0.0),
            PetState.SEEK_SHELTER: 0.05 + (0.92 if weather == "rain" else 0.0),
        }
        return u

    def tick(self, dt: float, weather: str, minute: int, player_space: str) -> dict[str, dict[str, object]]:
        result: dict[str, dict[str, object]] = {}
        for pet in self.pets.values():
            pet.action_age += dt
            if pet.action_age >= 3.0 + self._rng.random() * 4.0:
                utilities = self._utilities(pet, weather, minute, player_space)
                ranked = sorted(utilities.items(), key=lambda kv: kv[1] + self._rng.uniform(-0.055, 0.055), reverse=True)
                pet.state = ranked[0][0]
                pet.action_age = 0.0
            result[pet.pet_id] = {
                "space_id": pet.space_id,
                "state": pet.state.value,
                "action_age": round(pet.action_age, 2),
            }
        return result
