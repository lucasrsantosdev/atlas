"""Deterministic robot simulator with ACK deduplication and fault injection."""
from __future__ import annotations
from .protocol import Command, Acknowledgement, Telemetry
from .safety import RoboticsSafety
import time

class RobotSimulator:
    def __init__(self, device: str = "atlas-mini-sim", *, safety=None, clock=None):
        self.device = device
        self.clock = clock or time.monotonic
        self.safety = safety or RoboticsSafety(clock=self.clock)
        self.joints = {"head":90.0}
        self.led = False
        self.online = True
        self.sequence = 0
        self._acks: dict[str,Acknowledgement] = {}

    def execute(self, command: Command) -> Acknowledgement:
        if command.device != self.device: raise ValueError("wrong device")
        if command.request_id in self._acks: return self._acks[command.request_id]
        if not self.online: raise ConnectionError("simulated link down")
        if command.action == "estop":
            self.safety.stop();self.led = False
            ack = Acknowledgement(command.request_id, True, "stopped")
        else:
            self.safety.check()
            if command.action == "servo":
                joint,angle = command.args.get("joint"),command.args.get("angle")
                if joint not in self.joints or isinstance(angle,bool) or not isinstance(angle,(int,float)) or not 30 <= angle <= 150:
                    raise ValueError("invalid servo command")
                self.joints[joint] = float(angle)
            elif command.action == "led":
                if not isinstance(command.args.get("on"),bool): raise ValueError("invalid LED command")
                self.led = command.args["on"]
            elif command.action == "heartbeat": self.safety.heartbeat()
            else: raise ValueError("unknown action")
            ack = Acknowledgement(command.request_id,True,"ok")
        self._acks[command.request_id] = ack
        return ack

    def telemetry(self) -> Telemetry:
        self.sequence += 1
        return Telemetry(self.device,self.clock(),self.sequence,{"joints":dict(self.joints),"led":self.led,"stopped":self.safety.latched,"online":self.online})


    def set_online(self, online: bool):
        if not isinstance(online, bool):
            raise ValueError("online must be boolean")
        self.online = online

    def inject_sensor_fault(self, name: str):
        if not name:
            raise ValueError("sensor name required")
        self.safety.fail("sensor:" + name)
