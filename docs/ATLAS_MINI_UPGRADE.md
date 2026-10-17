# Atlas Mini V2 — incremental integration

## Scope delivered
- ESP32 simulator emergency-stop propagation from HardwareGateway, with a latched simulated device.
- Finite servo-angle validation (NaN and infinity rejected).
- Optional Whisper.cpp WAV transcription adapter, Piper WAV synthesis adapter, and local Ollama chat adapter.
- Focused tests for safety and provider contracts.

## Important safety boundary
Software E-stop is **not** a safety-rated stop. On real hardware, implement an independent power cutoff for motors, physical reset, watchdog, current limiting, and mechanical travel limits. The ESP32 firmware is bench-only. Software reset never clears the device's physical stop latch.

## Offline audio setup (operator-supplied binaries/models)
WhisperCppSTT(binary='whisper-cli', model='/models/ggml-base.bin') accepts WAV bytes. PiperTTS(binary='piper', model='/models/pt_BR.onnx') returns WAV bytes. OllamaResponder(model='qwen2.5:3b') talks only to http://127.0.0.1:11434/api/chat by default. All adapters are optional; nothing downloads automatically. Validate your installed CLI versions and model licenses.

## Example wiring
```python
from atlas.embodiment.session import VoiceSession
from atlas.embodiment.providers import WhisperCppSTT, PiperTTS, OllamaResponder
session = VoiceSession(
    stt=WhisperCppSTT('whisper-cli', '/models/ggml-base.bin'),
    tts=PiperTTS('piper', '/models/pt_BR.onnx'),
    responder=OllamaResponder('qwen2.5:3b'),
)
# answer, speech_wav = session.process(wav_bytes)
```

## Not yet delivered
- Physical ESP32/servo validation; no physical safety certification.
- Microphone capture, streaming speech, lip sync, sensor fusion, full motion planner.
- Hardware-independent measured maturity percentages. Prior maturity estimates remain qualitative.

## Verification
`python -m pytest -q` and `python -m compileall -q src`.
