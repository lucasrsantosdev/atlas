# Atlas — Cognitive Execution Loop, LLM goal boundary, ESP32 simulation

## Scope

Incremental, opt-in software-only delivery. No existing file is overwritten.

- `src/atlas/robotics/cognition/execution_loop.py`: bounded plan → observe → simulate → record → fallback. Callback `execute` must be **simulation only** until an independently reviewed physical safety layer is available. Limits: steps and replans. Per-session episodic records.
- `src/atlas/robotics/cognition/llm_goals.py`: injectable text-model protocol. Strict JSON proposal schema; allowlisted goals and confidence threshold. An LLM cannot specify raw motor commands. No actual model provider is bundled.
- `src/atlas/robotics/esp32_contract.py`: versioned CRC32 frame, monotonic sequence and explicit joint limits; simulated ESP32 and client using a transport protocol. This is **not firmware**, a serial driver, or physical safety protection.
- `src/atlas/embodiment/cognitive_expression.py`: opt-in adapter connecting text-derived affect to a symbolic gesture trajectory.
- `tests/test_cognitive_execution_llm_esp32.py`: unit and simulated contract tests.

## Physical hardware gate (not completed)

Before connecting actuators: independent hardware E-stop that removes power, mechanical end-stop verification, joint calibration, power/current limits, MCU watchdog and safe-stop behavior, emergency recovery procedure, serial protocol integration tests, collision analysis and supervised bench testing. Software ACK is not a safety guarantee. Never connect a motor to an unverified power stage.

## LLM integration gate (partially completed)

The adapter accepts a `generate(prompt)->str` model, including fakes in tests. Actual Ollama/remote LLM connection, schema reliability under real inference, adversarial prompt testing, timeouts and observability are pending.

## Acceptance criteria

1. Full pytest regression suite passes in user's Python 3.13 environment.
2. Invalid/unauthorized LLM output is rejected.
3. Symbolic loop terminates within bounded steps/replans; failure, cancellation, unsafe observations tested.
4. ESP32 simulated transport rejects replay, CRC mismatch and out-of-range joint positions.
5. No hardware I/O in this delivery.

## Apply

Extract ZIP at repository root, then:

```powershell
$env:PYTHONPATH = 'src'
py -3.13 -m pytest -q
```

Inspect `git status --short` before staging. Maturity percentages are targets, not verified measurement.
