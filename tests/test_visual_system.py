from awake_world.design.massing import (
    HUMAN_SCALE_UNITS,
    SPACE_MASSING_PROFILES,
)
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


def test_mvd1_massing_profiles_cover_every_registered_space() -> None:
    assert set(SPACE_MASSING_PROFILES) == set(SPACE_CATALOG)


def test_mvd1_spaces_have_unique_spatial_signatures() -> None:
    signatures: set[tuple[object, ...]] = set()
    landmarks: set[str] = set()

    for space_id, profile in SPACE_MASSING_PROFILES.items():
        signature = (
            profile.width_tiles,
            profile.depth_tiles,
            profile.axis,
            profile.landmark,
            len(profile.circulation),
            len(profile.volumes),
            round(sum(volume.w * volume.d for volume in profile.volumes), 1),
        )
        assert signature not in signatures, space_id
        assert profile.landmark not in landmarks, space_id
        signatures.add(signature)
        landmarks.add(profile.landmark)


def test_mvd1_scale_negative_space_and_landmarks_are_valid() -> None:
    for space_id, profile in SPACE_MASSING_PROFILES.items():
        assert profile.width_tiles >= 15, space_id
        assert profile.depth_tiles >= 12, space_id
        assert len(profile.circulation) >= 2, space_id
        assert profile.landmark_volumes, space_id

        spawn_x, spawn_y = profile.spawn
        assert 0.35 <= spawn_x <= profile.width_tiles - 0.35, space_id
        assert 0.35 <= spawn_y <= profile.depth_tiles - 0.35, space_id

        built_area = 0.0
        max_height = 0.0
        for volume in profile.volumes:
            assert volume.role in {"support", "primary", "landmark"}, space_id
            assert volume.w > 0 and volume.d > 0 and volume.h > 0, space_id
            assert volume.x >= -0.5 and volume.y >= -0.5, space_id
            assert volume.x + volume.w <= profile.width_tiles + 0.5, space_id
            assert volume.y + volume.d <= profile.depth_tiles + 0.5, space_id
            built_area += volume.w * volume.d
            max_height = max(max_height, volume.h)

            clear_x = volume.x - 0.18 <= spawn_x <= volume.x + volume.w + 0.18
            clear_y = volume.y - 0.18 <= spawn_y <= volume.y + volume.d + 0.18
            assert not (clear_x and clear_y), f"{space_id}: spawn intersects massing"

        assert max_height >= HUMAN_SCALE_UNITS * 1.05, space_id
        assert built_area / (profile.width_tiles * profile.depth_tiles) < 0.55, space_id


def test_mvd1_circulation_stays_inside_space_bounds() -> None:
    for space_id, profile in SPACE_MASSING_PROFILES.items():
        for band in profile.circulation:
            assert band.w >= 1.0 and band.d >= 1.0, space_id
            assert band.x >= 0 and band.y >= 0, space_id
            assert band.x + band.w <= profile.width_tiles, space_id
            assert band.y + band.d <= profile.depth_tiles, space_id
