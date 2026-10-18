from atlas.robotics.controller import RobotController
from atlas.robotics.simulator import RobotSimulator
from atlas.robotics.tools import register_robot_tools
from atlas.security import Permission,PolicyEngine
from atlas.tools.registry import ToolRegistry


def test_tools_deny_by_default_and_require_approval():
    sim=RobotSimulator();controller=RobotController(sim);controller.connect()
    registry=ToolRegistry(PolicyEngine(allowed={Permission.HARDWARE_READ}))
    register_robot_tools(registry,controller)
    assert registry.execute('robot.status').success
    denied=registry.execute('robot.led',on=True)
    assert not denied.success
    assert not sim.led


def test_tools_approved_actuation():
    sim=RobotSimulator();controller=RobotController(sim);controller.connect()
    policy=PolicyEngine(allowed={Permission.HARDWARE_READ,Permission.HARDWARE_WRITE})
    registry=ToolRegistry(policy);register_robot_tools(registry,controller)
    assert not registry.execute('robot.led',on=True).success
    token=policy.issue_approval(Permission.HARDWARE_WRITE,scope='robot.led')
    assert registry.execute('robot.led',on=True,approval_token=token).success
    assert sim.led
    assert not registry.execute('robot.led',on=False,approval_token=token).success
    assert registry.execute('robot.estop').success
    assert not registry.execute('robot.led',on=True,confirmed=True).success
