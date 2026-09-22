from awake_world.simulation.replay import SimulationRecorder, SimulationReplay


def test_replay_roundtrip_shape():
    r = SimulationRecorder(404)
    r.record(1, {"x": 1}, {"p": {"state": "walk"}}, [{"kind": "TIME_CHANGED"}], [])
    replay = SimulationReplay(r.to_dict())
    assert replay.seed == 404
    f = replay.next_frame()
    assert f["tick"] == 1
    assert replay.next_frame() is None
