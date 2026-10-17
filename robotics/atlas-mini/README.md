# Atlas Mini V1 — bench prototype

This is a **bench-only experimental integration**. It is not certified for a moving robot.

## Architecture

- Atlas Core runs on the PC; `HardwareGateway` checks capabilities and motion bounds.
- `SerialTransport` uses JSON-lines at 115200 baud, requires optional `pyserial`.
- ESP32 firmware (`firmware/atlas_mini_esp32.ino`) uses Arduino framework, ArduinoJson 7, ESP32Servo.
- `VoiceSession` offers dependency-injected STT/LLM/TTS interfaces; real Whisper/Piper adapters are **not implemented**.

## Wiring (bench, unloaded servo)

- ESP32 GPIO18 -> servo signal; servo power -> **separate regulated 5V supply**; connect grounds.
- GPIO2 -> onboard LED where present (board-dependent).
- Use a physical power disconnect/emergency switch. Do **not** power a servo from ESP32 3.3V.
- Disconnect servo during first serial tests. Never attach moving limbs until hardware safety review.

## PC smoke test (after flashing)

```python
from atlas.hardware.gateway import HardwareGateway, Device
from atlas.hardware.serial_transport import SerialTransport

gw = HardwareGateway()
gw.register(Device('mini', frozenset({'device.health','led.control','servo.set_angle','robot.estop'})))
gw.transport = SerialTransport('COM3')  # adjust port
print(gw.execute('mini', 'device.health'))
print(gw.execute('mini', 'servo.set_angle', angle=90))
```

**Safety caveats:** Software emergency stop in the gateway is local only; use `robot.estop` to latch firmware stop. Neither replaces a physical E-stop or motor power cut. Firmware currently holds servo position after link timeout; fail-safe behavior must be engineered and verified for the actual mechanics. The firmware's E-stop requires power cycle to reset; do not treat this as a safety-rated controller.

## Tests

`python -m pytest tests/test_atlas_mini_v1.py` (requires pytest)
