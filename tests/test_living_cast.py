from __future__ import annotations

from awake_world.design.characters import (
    CAIO_MONKS, DIRECTIONS, POSES, direction_from_vector,
    get_character_profile, validate_character_profiles,
)


def test_living_cast_profile_contract() -> None:
    assert validate_character_profiles() == ()
    assert get_character_profile("caio_monks") is CAIO_MONKS
    assert CAIO_MONKS.display_name == "Caio / MONKS"
    assert CAIO_MONKS.accessory == "headphones"
    assert CAIO_MONKS.metrics.height_px > CAIO_MONKS.metrics.width_px


def test_living_cast_has_eight_directions() -> None:
    expected = {
        (1, 0): "east", (1, -1): "north_east", (0, -1): "north",
        (-1, -1): "north_west", (-1, 0): "west", (-1, 1): "south_west",
        (0, 1): "south", (1, 1): "south_east",
    }
    assert len(DIRECTIONS) == 8
    assert len(set(DIRECTIONS)) == 8
    assert {vector: direction_from_vector(*vector) for vector in expected} == expected


def test_living_cast_required_poses_are_canonical() -> None:
    assert {"standing", "seated", "working", "listening", "resting", "phone"} <= set(POSES)
