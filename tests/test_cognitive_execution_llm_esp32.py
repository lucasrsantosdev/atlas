import json
import pytest
from atlas.robotics.cognition.hierarchical_planner import HierarchicalPlanner, Task
from atlas.robotics.cognition.execution_loop import CognitiveExecutionLoop
from atlas.robotics.cognition.llm_goals import LLMGoalAdapter
from atlas.robotics.esp32_contract import JointCommand, encode_command, decode_command, SimulatedESP32, ESP32Client
from atlas.embodiment.cognitive_expression import CognitiveExpression


def make_loop(**kwargs):
    p = HierarchicalPlanner({'greet': Task('greet', (Task('look'), Task('nod')))}, {'look', 'nod', 'neutral'})
    return CognitiveExecutionLoop(p, **kwargs)


def test_loop_success_and_memory():
    loop = make_loop()
    r = loop.run('greet', session='a', execute=lambda a: True)
    assert r.status == 'completed' and r.completed == ('look', 'nod')
    assert len(loop.memory.recent('a')) == 2
    assert loop.memory.recent('b') == ()


def test_loop_failure_and_fallback():
    loop = make_loop()
    r = loop.run('greet', session='a', execute=lambda a: a != 'look', fallback={'look': ('neutral',)})
    assert r.status == 'completed' and r.replans == 1
    assert r.attempted == ('look', 'neutral', 'nod')


def test_loop_failure_without_fallback():
    assert make_loop().run('greet', session='a', execute=lambda a: False).status == 'failed'


def test_loop_budget():
    assert make_loop(max_steps=1).run('greet', session='a', execute=lambda a: True).status == 'budget_exceeded'


def test_loop_cancel():
    assert make_loop().run('greet', session='a', execute=lambda a: True, cancelled=lambda: True).status == 'cancelled'


def test_loop_observation_blocks():
    assert make_loop().run('greet', session='a', execute=lambda a: True, observe=lambda: False).status == 'blocked'


def test_loop_fallback_denied():
    with pytest.raises(ValueError):
        make_loop().run('greet', session='a', execute=lambda a: False, fallback={'look': ('unsafe',)})


class FakeModel:
    def __init__(self, response): self.response = response
    def generate(self, prompt): return self.response


def test_llm_authorized_goal():
    adapter = LLMGoalAdapter(FakeModel(json.dumps({'goal': 'greet', 'confidence': 0.9, 'reason': 'requested'})), frozenset({'greet'}))
    assert adapter.propose('hello').goal == 'greet'


@pytest.mark.parametrize('payload', ['not json', '{}', '{"goal":"raw_motor","confidence":1,"reason":"x"}', '{"goal":"greet","confidence":0.1,"reason":"x"}', '{"goal":"greet","confidence":true,"reason":"x"}'])
def test_llm_rejects_invalid(payload):
    with pytest.raises(ValueError):
        LLMGoalAdapter(FakeModel(payload), frozenset({'greet'})).propose('hello')


def test_esp32_roundtrip():
    cmd = JointCommand(1, 'head', 90.0)
    assert decode_command(encode_command(cmd)) == cmd


def test_esp32_checksum():
    packet = encode_command(JointCommand(1, 'head', 90))
    with pytest.raises(ValueError): decode_command(packet.replace(b'head', b'hand'))


def test_esp32_ack_and_replay():
    sim = SimulatedESP32({'head': (40, 140)})
    client = ESP32Client(sim, allowed_joints=frozenset({'head'}), limits={'head': (40, 140)})
    cmd = JointCommand(1, 'head', 90)
    assert client.send(cmd) is True
    assert client.send(cmd) is False
    assert sim.positions['head'] == 90


def test_esp32_limits():
    client = ESP32Client(SimulatedESP32({'head': (40, 140)}), allowed_joints=frozenset({'head'}), limits={'head': (40, 140)})
    with pytest.raises(ValueError): client.send(JointCommand(1, 'head', 170))


def test_esp32_fault():
    sim = SimulatedESP32({'head': (40, 140)})
    sim.enabled = False
    assert not ESP32Client(sim, allowed_joints=frozenset({'head'}), limits={'head': (40, 140)}).send(JointCommand(1, 'head', 90))


def test_expression_is_symbolic():
    decision = CognitiveExpression().plan('I am happy!', {'head': 90.0})
    assert decision.behavior.trajectory
