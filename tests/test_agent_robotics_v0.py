from atlas.agent import AgentLoop, PlannedToolCall
from atlas.mosaic.models import MosaicRequest
from atlas.mosaic.service import MosaicService
from atlas.observability import AuditTrail
from atlas.robotics import SimulatedHardware, register_simulated_robotics
from atlas.security import Permission, PolicyEngine
from atlas.tools.registry import ToolRegistry


def make_loop(permissions=()):
    registry = ToolRegistry(PolicyEngine(allowed=set(permissions)))
    hardware = SimulatedHardware()
    register_simulated_robotics(registry, hardware)
    trail = AuditTrail()
    return AgentLoop(MosaicService(), registry, trail, max_steps=2), hardware, trail


def test_analysis_alone_executes_nothing():
    loop, hw, trail = make_loop()
    out = loop.run(MosaicRequest("Olá Atlas"))
    assert out.stopped_reason == "analysis_only"
    assert out.results == ()
    assert hw.outputs == {}
    assert len(trail.events()) == 1


def test_read_requires_hardware_permission():
    loop, _, _ = make_loop()
    out = loop.run(MosaicRequest("Leia a temperatura"), (PlannedToolCall("robot.sim.read", {"sensor": "temperature"}),))
    assert not out.results[0].success
    assert out.stopped_reason == "tool_failed_or_denied"


def test_read_is_allowed_with_permission():
    loop, _, _ = make_loop((Permission.HARDWARE_READ,))
    out = loop.run(MosaicRequest("Leia a temperatura"), (PlannedToolCall("robot.sim.read", {"sensor": "temperature"}),))
    assert out.results[0].success
    assert out.results[0].output == "22.0"


def test_write_requires_confirmation_even_with_permission():
    loop, hw, _ = make_loop((Permission.HARDWARE_WRITE,))
    out = loop.run(MosaicRequest("Acenda o LED"), (PlannedToolCall("robot.sim.write", {"channel": "led", "value": 1.0}),))
    assert not out.results[0].success
    assert hw.outputs == {}


def test_write_confirmed_changes_simulator():
    loop, hw, _ = make_loop((Permission.HARDWARE_WRITE,))
    out = loop.run(MosaicRequest("Acenda o LED"), (PlannedToolCall("robot.sim.write", {"channel": "led", "value": 1.0}, confirmed=True),))
    assert out.stopped_reason == "completed"
    assert hw.outputs["led"] == 1.0


def test_invalid_actuator_value_does_not_write():
    loop, hw, _ = make_loop((Permission.HARDWARE_WRITE,))
    out = loop.run(MosaicRequest("Acenda o LED"), (PlannedToolCall("robot.sim.write", {"channel": "led", "value": 10}, confirmed=True),))
    assert not out.results[0].success
    assert hw.outputs == {}


def test_step_limit_blocks_without_execution():
    loop, hw, trail = make_loop((Permission.HARDWARE_WRITE,))
    step = PlannedToolCall("robot.sim.write", {"channel": "led", "value": 1.0}, confirmed=True)
    out = loop.run(MosaicRequest("Acenda o LED"), (step, step, step))
    assert out.stopped_reason == "max_steps_exceeded"
    assert hw.outputs == {}
    assert trail.events()[-1].event == "agent.limit"


def test_unknown_tool_is_denied():
    loop, _, _ = make_loop()
    out = loop.run(MosaicRequest("Execute"), (PlannedToolCall("not.registered"),))
    assert not out.results[0].success


def test_audit_does_not_store_user_text():
    loop, _, audit = make_loop()
    loop.run(MosaicRequest("Minha senha é muito-secreta"))
    assert "muito-secreta" not in repr(audit.events())


def test_no_implicit_robot_execution_from_user_text():
    loop, hw, _ = make_loop((Permission.HARDWARE_WRITE,))
    out = loop.run(MosaicRequest("Acenda o LED agora"))
    assert out.stopped_reason == "analysis_only"
    assert hw.outputs == {}
