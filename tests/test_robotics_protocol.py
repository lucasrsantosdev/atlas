import pytest
from atlas.robotics.protocol import Command,ProtocolError
from atlas.robotics.controller import RobotController,RobotState
from atlas.robotics.simulator import RobotSimulator
from atlas.robotics.motion import MotionPlanner,JointLimit,MotionStep
from atlas.robotics.safety import RoboticsSafety
from atlas.robotics.sensors import SensorHub,SensorSample


def test_protocol_rejects_unsupported_version():
    with pytest.raises(ProtocolError): Command('sim','led',version='v99')


def test_deduplicates_request_id():
    sim=RobotSimulator()
    cmd=Command(sim.device,'led',{'on':True})
    assert sim.execute(cmd)==sim.execute(cmd)
    assert sim.led is True


def test_retry_preserves_id():
    sim=RobotSimulator()
    class Flaky:
        def __init__(self):self.ids=[]
        def execute(self,cmd):
            self.ids.append(cmd.request_id)
            if len(self.ids)==1:raise TimeoutError('lost ACK')
            return sim.execute(cmd)
    f=Flaky();controller=RobotController(f)
    controller.connect()
    assert len(set(f.ids))==1


def test_motion_and_estop():
    sim=RobotSimulator();controller=RobotController(sim)
    controller.connect()
    planner=MotionPlanner({'head':JointLimit(max_delta=20)})
    assert controller.move(planner,[MotionStep('head',100),MotionStep('head',90)])==2
    assert sim.joints['head']==90
    controller.emergency_stop()
    with pytest.raises(PermissionError):controller.send('led',on=True)
    assert sim.telemetry().values['stopped']


def test_motion_limits_reject_entire_plan_before_actuation():
    sim=RobotSimulator();controller=RobotController(sim);controller.connect()
    with pytest.raises(ValueError):controller.move(MotionPlanner({'head':JointLimit(max_delta=20)}),[MotionStep('head',100),MotionStep('head',150)])
    assert sim.joints['head']==90


def test_watchdog_latches_and_requires_local_confirmation():
    now=[0.0]
    safety=RoboticsSafety(watchdog_seconds=2,clock=lambda:now[0]);now[0]=3
    with pytest.raises(PermissionError):safety.check()
    with pytest.raises(PermissionError):safety.reset()
    safety.reset(local_operator_confirmed=True)
    safety.check()


def test_sensor_hub_rejects_stale():
    hub=SensorHub(2);hub.publish(SensorSample('temp',24,'C',10))
    with pytest.raises(ValueError):hub.publish(SensorSample('temp',22,'C',9))
    assert hub.snapshot()['temp'].value==24


def test_offline_device():
    sim=RobotSimulator();sim.online=False
    with pytest.raises(ConnectionError):RobotController(sim,retries=1).connect()
