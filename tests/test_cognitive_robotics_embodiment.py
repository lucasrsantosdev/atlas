import pytest
from atlas.robotics.cognition import BehaviorPlanner, Intent, GoalManager, Goal, ExperienceMemory, ActionSelector
from atlas.robotics.cognition.experience_memory import Experience
from atlas.robotics.cognition.behavior_tree import Condition, All, Any
from atlas.robotics.safety import RoboticsSafety
from atlas.embodiment.emotion import EmotionInterpreter
from atlas.embodiment.personality import Personality
from atlas.embodiment.gesture_generator import GestureGenerator

@pytest.mark.parametrize('name', ['acknowledge','look_left','look_right','neutral','express_happiness'])
def test_planner_safe_and_pure(name):
    joints={'head':90.0}; plan=BehaviorPlanner().plan(Intent(name,0.7),joints)
    assert plan.trajectory and all(30<=step.angle<=150 for step in plan.trajectory)
    assert joints=={'head':90.0}

def test_dynamic_intensity_changes_target():
    planner=BehaviorPlanner()
    low=planner.plan(Intent('look_left',0.2),{'head':90.})
    high=planner.plan(Intent('look_left',0.8),{'head':90.})
    assert high.trajectory[-1].angle < low.trajectory[-1].angle

def test_safety_latch_blocks_plan():
    safety=RoboticsSafety(); safety.stop()
    with pytest.raises(PermissionError): BehaviorPlanner().plan(Intent('neutral'),{'head':90.},safety=safety)

@pytest.mark.parametrize('intensity', [-1,2,float('nan'),float('inf'),True])
def test_reject_invalid_intensity(intensity):
    with pytest.raises(ValueError): Intent('neutral',intensity)

def test_reject_unapproved_intent():
    with pytest.raises(ValueError): BehaviorPlanner().plan(Intent('spin'),{'head':90.})

def test_goal_priorities_and_removal():
    g=GoalManager();g.add(Goal('observe',1));g.add(Goal('stop',10))
    assert g.next_goal().name=='stop'
    g.remove('stop');assert g.next_goal().name=='observe'

def test_experience_ranking_is_bounded():
    m=ExperienceMemory(2)
    m.record(Experience('greet','nod',False))
    m.record(Experience('greet','wave',True))
    assert ActionSelector(m).select('greet',('nod','wave'))=='wave'
    m.record(Experience('greet','nod',True));assert len(m.recent())==2

def test_behavior_tree():
    tree=All((Condition(lambda c:c['ready']),Any((Condition(lambda c:c['safe']),Condition(lambda c:c['override'])))))
    assert tree.evaluate({'ready':True,'safe':True,'override':False})
    assert not tree.evaluate({'ready':False,'safe':True,'override':True})

def test_emotion_to_contextual_motion():
    g=GestureGenerator()
    happy=g.generate('estou feliz',{'head':90.},personality=Personality(expressiveness=1.))
    neutral=g.generate('bom dia',{'head':90.})
    assert happy.intent.name=='express_happiness'
    assert happy.trajectory[-1].angle>neutral.trajectory[-1].angle

def test_unknown_text_is_neutral():
    assert EmotionInterpreter().interpret('oi tudo bem').label=='neutral'

def test_personality_zero_expression():
    result=GestureGenerator().generate('feliz',{'head':90.},personality=Personality(expressiveness=0.))
    assert result.trajectory[-1].angle==90.
