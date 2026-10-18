import pytest
from atlas.robotics.cognition.hierarchical_planner import Task, HierarchicalPlanner
from atlas.robotics.cognition.decision_evaluator import Candidate, DecisionEvaluator
from atlas.robotics.cognition.episodic_memory import Episode, EpisodicMemory
from atlas.robotics.cognition.scenario_runner import ScenarioRunner


def planner():
    return HierarchicalPlanner({'greet': Task('greet', (Task('look_left'), Task('acknowledge'), Task('neutral')))},
                               {'look_left', 'acknowledge', 'neutral'})

def test_hierarchical_order():
    assert planner().plan('greet').actions == ('look_left', 'acknowledge', 'neutral')

def test_unknown_goal():
    with pytest.raises(ValueError, match='unknown goal'): planner().plan('missing')

def test_reject_unapproved_leaf():
    with pytest.raises(ValueError, match='not allowed'):
        HierarchicalPlanner({'x': Task('danger')}, {'neutral'}).plan('x')

def test_depth_budget():
    with pytest.raises(ValueError, match='depth'):
        HierarchicalPlanner({'x': Task('x', (Task('middle', (Task('neutral'),)),))}, {'neutral'}, max_depth=1).plan('x')

def test_action_budget():
    with pytest.raises(ValueError, match='budget'):
        HierarchicalPlanner({'x': Task('x', (Task('neutral'), Task('neutral')))}, {'neutral'}, max_actions=1).plan('x')

def test_cycle_rejected():
    t = Task('x')
    object.__setattr__(t, 'children', (t,))
    with pytest.raises(ValueError, match='cyclic'):
        HierarchicalPlanner({'x': t}, {'neutral'}).plan('x')

def test_invalid_task():
    with pytest.raises(ValueError): Task('')

def test_evaluator_prefers_safe():
    d = DecisionEvaluator().choose((Candidate('unsafe', 100, 0.8, 1), Candidate('safe', 2, 0.1, 1)), allowed_actions=frozenset({'unsafe','safe'}))
    assert d.action == 'safe'

def test_evaluator_rejects_unauthorized():
    with pytest.raises(ValueError, match='no safe'):
        DecisionEvaluator().choose((Candidate('a', 1, 0, 0),), allowed_actions=frozenset({'b'}))

def test_evaluator_tiebreak():
    d = DecisionEvaluator().choose((Candidate('first', 1, 0, 0), Candidate('second', 1, 0, 0)), allowed_actions=frozenset({'first','second'}))
    assert d.action == 'first'

def test_evaluator_nonfinite():
    with pytest.raises(ValueError): Candidate('x', float('nan'), 0, 0)

def test_memory_isolated():
    m = EpisodicMemory()
    m.record(Episode('a', 'g', 'x', True, 2))
    m.record(Episode('b', 'g', 'x', False, -1))
    assert len(m.recent('a')) == 1
    assert m.stats('a', 'g', 'x') == (1, 1, 2)
    assert m.stats('b', 'g', 'x') == (1, 0, -1)

def test_memory_bounded():
    m = EpisodicMemory(1)
    m.record(Episode('a', 'g', 'x', True, 1))
    m.record(Episode('a', 'g', 'y', False, 0))
    assert len(m.recent('a')) == 1
    assert m.stats('a','g','x')[0] == 0

def test_memory_empty_stats():
    assert EpisodicMemory().stats('a','b','c') == (0,0,0)

def test_memory_invalid_reward():
    with pytest.raises(ValueError): Episode('a','g','x',True,float('inf'))

def test_scenario_complete():
    r = ScenarioRunner(planner()).run('greet')
    assert r.status == 'completed' and len(r.completed) == 3

def test_scenario_failure():
    r = ScenarioRunner(planner()).run('greet', fail_at=1)
    assert r.status == 'failed' and r.completed == ('look_left',)

def test_scenario_cancel():
    r = ScenarioRunner(planner()).run('greet', cancel_at=0)
    assert r.status == 'cancelled' and not r.attempted

def test_scenario_invalid_fault_index():
    with pytest.raises(ValueError): ScenarioRunner(planner()).run('greet', fail_at=-1)
