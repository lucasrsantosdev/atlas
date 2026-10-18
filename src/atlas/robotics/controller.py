"""Bounded retries, cancellation and state transitions for a robot transport."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .protocol import Command, Acknowledgement
from .motion import MotionPlanner, MotionStep

class RobotState(str,Enum): DISCONNECTED="disconnected";READY="ready";STOPPED="stopped"

class RobotController:
    def __init__(self, transport, *, device="atlas-mini-sim", retries=2):
        if retries < 0 or retries > 5: raise ValueError("retries must be 0..5")
        self.transport=transport;self.device=device;self.retries=retries
        self.state=RobotState.DISCONNECTED;self.cancelled=False

    def connect(self):
        self.send("heartbeat", allow_disconnected=True)
        self.state=RobotState.READY

    def send(self, action, *, allow_disconnected=False, **args):
        if self.state==RobotState.STOPPED and action!="estop": raise PermissionError("controller stopped")
        if self.state==RobotState.DISCONNECTED and not allow_disconnected and action!="estop": raise ConnectionError("not connected")
        cmd=Command(self.device,action,args)
        for attempt in range(self.retries+1):
            try:
                ack=self.transport.execute(cmd)
                if not isinstance(ack,Acknowledgement) or ack.request_id!=cmd.request_id or not ack.accepted:
                    raise RuntimeError("invalid or rejected acknowledgment")
                return ack
            except (ConnectionError,TimeoutError):
                if attempt==self.retries:
                    self.state=RobotState.DISCONNECTED
                    raise
        raise RuntimeError("unreachable")

    def move(self, planner:MotionPlanner, steps:list[MotionStep]):
        if self.state!=RobotState.READY: raise RuntimeError("robot not ready")
        planned=planner.plan(steps,self.transport.joints)
        self.cancelled=False
        completed=0
        for step in planned:
            if self.cancelled: break
            self.send("servo",joint=step.joint,angle=step.angle)
            completed+=1
        return completed

    def cancel(self): self.cancelled=True

    def emergency_stop(self):
        self.state=RobotState.STOPPED
        self.cancelled=True
        return self.send("estop")


    def recover(self, *, local_operator_confirmed: bool = False):
        if not local_operator_confirmed:
            raise PermissionError("operator confirmation required")
        if hasattr(self.transport, "safety"):
            self.transport.safety.reset(local_operator_confirmed=True)
        self.state = RobotState.DISCONNECTED
        self.cancelled = False
        self.connect()
