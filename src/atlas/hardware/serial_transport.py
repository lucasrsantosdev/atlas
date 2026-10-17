"""Opt-in JSON-lines serial transport. Requires pip install pyserial."""
from __future__ import annotations
import json
import threading
from .gateway import HardwareMessage

class SerialTransport:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 2.0):
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("Install pyserial to use physical ESP32") from exc
        self._serial = serial.Serial(port, baudrate=baudrate, timeout=timeout, write_timeout=timeout)
        self._lock = threading.Lock()

    def request(self, message: HardwareMessage):
        payload = {"protocol": message.protocol, "device": message.device,
                   "request_id": message.request_id, "capability": message.capability,
                   "arguments": message.arguments}
        with self._lock:
            self._serial.write((json.dumps(payload, separators=(",", ":")) + "\n").encode())
            raw = self._serial.readline()
        if not raw:
            raise TimeoutError("ESP32 did not respond")
        response = json.loads(raw)
        if response.get("request_id") != message.request_id:
            raise RuntimeError("ESP32 response request_id mismatch")
        if not response.get("ok", False):
            raise RuntimeError(str(response.get("error", "ESP32 command failed")))
        return response.get("result")

    def close(self):
        self._serial.close()
