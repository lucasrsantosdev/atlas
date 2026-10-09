"""Contrato de hardware v0 e simulador; nenhum driver físico é carregado."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol

from atlas.security import Permission, RiskLevel
from atlas.tools.registry import ToolManifest, ToolRegistry, ToolResult

class HardwareAbstractionLayer(Protocol):
    def read_sensor(self, sensor: str) -> float: ...
    def set_output(self, channel: str, value: float) -> None: ...

@dataclass
class SimulatedHardware:
    sensors: dict[str, float] = field(default_factory=lambda: {"temperature": 22.0})
    outputs: dict[str, float] = field(default_factory=dict)

    def read_sensor(self, sensor: str) -> float:
        if sensor not in self.sensors:
            raise ValueError("unknown sensor")
        return self.sensors[sensor]

    def set_output(self, channel: str, value: float) -> None:
        if channel not in {"led", "servo"}:
            raise ValueError("unsupported channel")
        if not (0.0 <= value <= 1.0):
            raise ValueError("value must be between 0 and 1")
        self.outputs[channel] = value

def register_simulated_robotics(registry: ToolRegistry,
                                hardware: SimulatedHardware) -> None:
    registry.register(
        ToolManifest(name="robot.sim.read", description="Read simulated sensor",
                     permission=Permission.HARDWARE_READ, risk=RiskLevel.LOW),
        lambda sensor: ToolResult(success=True, output=str(hardware.read_sensor(sensor))),
    )
    registry.register(
        ToolManifest(name="robot.sim.write", description="Change simulated actuator",
                     permission=Permission.HARDWARE_WRITE, risk=RiskLevel.HIGH,
                     side_effects=True),
        lambda channel, value: _sim_write(hardware, channel, value),
    )

def _sim_write(hardware: SimulatedHardware, channel: str, value: float) -> ToolResult:
    hardware.set_output(channel, value)
    return ToolResult(success=True, output="simulated output updated")
