# Atlas quality gates — V3

A percentage of completion is **not** a validated quality score. Reaching 100% requires explicit acceptance evidence per subsystem.

| Subsystem | Minimum acceptance evidence |
|---|---|
| Foundation | Reproducible install, supported Python matrix, package/CLI smoke tests |
| Model Runtime | Two real providers, fallback, timeouts, resource benchmarks |
| Memory | Persistent reload, tenant isolation, retention and migration tests |
| Knowledge/RAG | Retrieval relevance dataset, citations, ingestion failure handling |
| Agent Loop/Mosaic | Multi-step scenario suite, bounded retries, cancellation and recovery |
| Tools/MCP | Real external MCP server interoperability, permissions and timeout tests |
| Security | Threat model, injection tests, audit verification and independent review |
| Observability | Trace correlation, redaction, metrics and export validation |
| Robotics | Firmware compile, serial loopback, watchdog, motor limits and failsafe tests |
| Embodiment | Offline real STT→LLM→TTS integration, latency, microphone and speaker validation |
| Physical hardware | Actual ESP32, independent actuator power cut, physical E-stop, measured tests |

## Safety caveat
The software E-stop is a *logical* interlock, not a certified or physically independent safety stop. No unreviewed LLM output should drive actuators directly. Never mark physical hardware as validated without real-world evidence.

## Running tests
`python -m pip install -e ".[dev]"` then `python -m pytest -q`.
