from awake_world.world.save import CURRENT_SAVE_SCHEMA, migrate_payload, _state_from_payload, state_payload


def test_v5_payload_migrates():
    old = {"version": 5, "last_room": "quarter", "weather": "rain", "inventory": []}
    migrated = migrate_payload(old)
    assert migrated["schema_version"] == CURRENT_SAVE_SCHEMA
    state = _state_from_payload(old)
    assert state.weather == "rain"
    payload = state_payload(state)
    assert payload["schema_version"] == CURRENT_SAVE_SCHEMA
    assert "world_seed" in payload and "environment_state" in payload


def test_player_state_roundtrip_uses_canonical_player_key():
    raw = {
        "schema_version": CURRENT_SAVE_SCHEMA,
        "last_room": "observatory",
        "player": {"space_id": "observatory", "position": [3.25, 4.5], "facing": [1.0, 0.0]},
    }
    state = _state_from_payload(raw)
    assert state.player_state["position"] == [3.25, 4.5]
    payload = state_payload(state)
    assert payload["player"]["space_id"] == "observatory"
    assert payload["player"]["facing"] == [1.0, 0.0]
