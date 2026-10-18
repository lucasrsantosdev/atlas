"""Policy-gated Atlas ToolRegistry integration. No direct LLM-to-actuator path."""
from atlas.security import Permission,RiskLevel
from atlas.tools.registry import ToolManifest

def register_robot_tools(registry, controller):
    registry.register(ToolManifest("robot.status","Read simulated robot state",Permission.HARDWARE_READ),
                      lambda: controller.transport.telemetry().values)
    registry.register(ToolManifest("robot.estop","Latch simulated robot stop",Permission.HARDWARE_WRITE,RiskLevel.LOW,side_effects=True,idempotent=True),
                      lambda: controller.emergency_stop().status)
    registry.register(ToolManifest("robot.led","Set simulated LED",Permission.HARDWARE_WRITE,RiskLevel.HIGH,side_effects=True,
                                   schema={"required":["on"]},idempotent=True),
                      lambda on: controller.send("led",on=on).status)
