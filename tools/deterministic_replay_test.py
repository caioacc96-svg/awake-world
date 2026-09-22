from __future__ import annotations

import json
from pathlib import Path
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from awake_world.presentation.transition_orchestrator import SpaceTransitionOrchestrator
from awake_world.simulation import ActorRuntime, SimulationRecorder, SimulationReplay, Vec2
from awake_world.world.state import WorldState
from awake_world.world.systems.runtime import WorldRuntime


def run_sequence(seed: int) -> dict:
    state=WorldState(world_seed=seed)
    world=WorldRuntime(state,minutes_per_real_second=1.0)
    actor=ActorRuntime('local_player',position=Vec2(5,5))
    transition=SpaceTransitionOrchestrator()
    recorder=SimulationRecorder(seed)
    for tick in range(180):
        if tick < 60: actor.set_input(1,0,False)
        elif tick < 120: actor.set_input(0,-1,True)
        else: actor.clear_input()
        actor.advance(1/60,lambda x,y: 0.2 < x < 20 and 0.2 < y < 20)
        if tick==70:
            world.set_weather('rain')
            transition.start('quarter','observatory','exterior_to_interior')
        if transition.active: transition.tick(1/60)
        world.tick(1/60)
        recorder.record(tick,{'dx':actor.input_direction.x,'dy':actor.input_direction.y}, {'player':actor.snapshot()}, [], [])
    return {'world':world.snapshot(),'actor':actor.snapshot(),'replay':recorder.to_dict()}


def main() -> int:
    a=run_sequence(404); b=run_sequence(404)
    assert a==b, 'deterministic sequence diverged for identical seed'
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'replay.json'
        r=SimulationRecorder(404); r.record(1,{'e':True},{'player':{'state':'interact'}}); r.write(p)
        replay=SimulationReplay.read(p)
        assert replay.next_frame()['tick']==1
    print('AWAKE_DETERMINISTIC_REPLAY_OK')
    print(json.dumps({'tick':a['world']['tick'],'weather':a['world']['weather'],'actor':a['actor']['state']}))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
