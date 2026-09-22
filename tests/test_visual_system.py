from awake_world.design.world_visuals import SPACE_VISUAL_PROFILES
from awake_world.world.systems.spaces import SPACE_CATALOG


def test_visual_profiles_cover_every_registered_space() -> None:
    assert set(SPACE_VISUAL_PROFILES) == set(SPACE_CATALOG)


def test_visual_profiles_are_valid_canonical_tokens() -> None:
    for profile in SPACE_VISUAL_PROFILES.values():
        assert profile.floor_family in {"plaza", "roof", "home", "warm"}
        for color in (
            profile.surface,
            profile.material,
            profile.structure,
            profile.accent,
            profile.accent_alt,
            profile.vegetation,
            profile.ambient,
            profile.label,
        ):
            assert len(color) == 7
            assert color.startswith("#")
            int(color[1:], 16)
        assert 0.0 <= profile.openness <= 1.0
        assert 0.0 <= profile.density <= 1.0


def test_architecture_profiles_do_not_use_banned_visual_shortcuts() -> None:
    banned = ("cyberpunk", "neon", "corporate_metaverse", "asset_store")
    for definition in SPACE_CATALOG.values():
        profile = definition.architecture_profile.lower()
        assert not any(token in profile for token in banned)
