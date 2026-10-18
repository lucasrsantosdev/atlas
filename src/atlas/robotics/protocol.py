"""Versioned, idempotent command envelope and acknowledgment semantics."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math
import uuid

VERSION = "atlas-robot/1"
class ProtocolError(ValueError): pass

@dataclass(frozen=True)
class Command:
    device: str
    action: str
    args: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = VERSION

    def __post_init__(self):
        if self.version != VERSION: raise ProtocolError("unsupported protocol version")
        if not self.device or not self.action or not self.request_id: raise ProtocolError("missing command field")
        if not isinstance(self.args, dict): raise ProtocolError("args must be an object")

@dataclass(frozen=True)
class Acknowledgement:
    request_id: str
    accepted: bool
    status: str
    error: str | None = None

@dataclass(frozen=True)
class Telemetry:
    device: str
    timestamp: float
    sequence: int
    values: dict[str, Any]

    def __post_init__(self):
        if not math.isfinite(self.timestamp) or self.sequence < 0: raise ProtocolError("invalid telemetry")


# Canonical, checksummed wire envelopes. CRC detects corruption, not malicious tampering.
import json
import zlib

MAX_FRAME_BYTES = 8192

def encode_command(command: Command, *, sequence: int) -> bytes:
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
        raise ProtocolError("invalid sequence")
    payload = {"version": command.version, "device": command.device, "action": command.action,
               "args": command.args, "request_id": command.request_id, "sequence": sequence}
    try:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ProtocolError("invalid command payload") from exc
    if len(raw) > MAX_FRAME_BYTES:
        raise ProtocolError("frame too large")
    return json.dumps({"payload": payload, "crc32": f"{zlib.crc32(raw):08x}"},
                      sort_keys=True, separators=(",", ":")).encode("utf-8")

def decode_command(frame: bytes) -> tuple[Command, int]:
    if not isinstance(frame, bytes) or len(frame) > MAX_FRAME_BYTES * 2:
        raise ProtocolError("invalid frame size")
    try:
        envelope = json.loads(frame)
        if not isinstance(envelope, dict) or set(envelope) != {"payload", "crc32"}:
            raise ValueError("invalid envelope")
        payload = envelope["payload"]
        if not isinstance(payload, dict) or set(payload) != {"version", "device", "action", "args", "request_id", "sequence"}:
            raise ValueError("invalid payload")
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        if len(raw) > MAX_FRAME_BYTES or envelope["crc32"] != f"{zlib.crc32(raw):08x}":
            raise ValueError("checksum mismatch")
        sequence = payload["sequence"]
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
            raise ValueError("invalid sequence")
        return Command(payload["device"], payload["action"], payload["args"],
                       payload["request_id"], payload["version"]), sequence
    except (UnicodeError, ValueError, TypeError, KeyError) as exc:
        raise ProtocolError("malformed or corrupted frame") from exc
