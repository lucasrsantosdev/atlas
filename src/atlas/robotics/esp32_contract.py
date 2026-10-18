"""ESP32 transport contract and simulator. Not a physical safety controller.

    Firmware must implement its own watchdog, limits and emergency stop.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
import json
import math
import zlib

class ByteTransport(Protocol):
    def exchange(self, payload: bytes) -> bytes: ...

@dataclass(frozen=True)
class JointCommand:
    sequence: int
    joint: str
    angle_deg: float

    def __post_init__(self):
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or not 0 <= self.sequence < 2**31:
            raise ValueError('invalid sequence')
        if not isinstance(self.joint, str) or not self.joint.isidentifier() or len(self.joint) > 32:
            raise ValueError('invalid joint')
        if isinstance(self.angle_deg, bool) or not isinstance(self.angle_deg, (int, float)) or not math.isfinite(self.angle_deg) or not 0 <= self.angle_deg <= 180:
            raise ValueError('invalid angle')

def encode_command(command: JointCommand) -> bytes:
    body = json.dumps({'v': 1, 'seq': command.sequence, 'joint': command.joint, 'angle': command.angle_deg},
                      sort_keys=True, separators=(',', ':')).encode('ascii')
    crc = zlib.crc32(body)
    return body + b'|' + f'{crc:08x}'.encode('ascii') + b'\n'

def decode_command(packet: bytes) -> JointCommand:
    if not isinstance(packet, bytes) or len(packet) > 256 or not packet.endswith(b'\n'):
        raise ValueError('invalid packet')
    try:
        body, crc = packet[:-1].rsplit(b'|', 1)
        if len(crc) != 8 or zlib.crc32(body) != int(crc, 16):
            raise ValueError('checksum mismatch')
        obj = json.loads(body)
        if not isinstance(obj, dict) or set(obj) != {'v', 'seq', 'joint', 'angle'} or obj['v'] != 1:
            raise ValueError('unsupported protocol')
        return JointCommand(obj['seq'], obj['joint'], obj['angle'])
    except (UnicodeError, ValueError, TypeError, KeyError) as exc:
        raise ValueError('invalid packet') from exc

class SimulatedESP32:
    """Strictly symbolic ACK emulator; no serial port or motor access."""
    def __init__(self, limits: dict[str, tuple[float, float]]):
        self.limits = dict(limits)
        self.last_sequence = -1
        self.positions: dict[str, float] = {}
        self.enabled = True

    def exchange(self, payload: bytes) -> bytes:
        if not self.enabled:
            return b'FAULT\n'
        try:
            cmd = decode_command(payload)
        except ValueError:
            return b'NACK\n'
        if cmd.sequence <= self.last_sequence:
            return b'NACK\n'
        bounds = self.limits.get(cmd.joint)
        if bounds is None or not bounds[0] <= cmd.angle_deg <= bounds[1]:
            return b'NACK\n'
        self.last_sequence = cmd.sequence
        self.positions[cmd.joint] = cmd.angle_deg
        return f'ACK:{cmd.sequence}\n'.encode('ascii')

class ESP32Client:
    def __init__(self, transport: ByteTransport, *, allowed_joints: frozenset[str], limits: dict[str, tuple[float, float]]):
        self.transport, self.allowed_joints, self.limits = transport, allowed_joints, limits

    def send(self, command: JointCommand) -> bool:
        if command.joint not in self.allowed_joints or command.joint not in self.limits:
            raise ValueError('joint not authorized')
        low, high = self.limits[command.joint]
        if not low <= command.angle_deg <= high:
            raise ValueError('joint limit exceeded')
        return self.transport.exchange(encode_command(command)) == f'ACK:{command.sequence}\n'.encode('ascii')
