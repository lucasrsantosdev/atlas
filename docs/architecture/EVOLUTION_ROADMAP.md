# ATLAS.IA Evolution Roadmap

## Architectural thesis
Atlas owns identity, memory, knowledge, policy and capabilities. Models, tools and hardware are replaceable providers.

## Current implementation baseline
This branch establishes the foundations for the consolidated roadmap: model runtime/Ollama, SQLite+FTS memory backend, searchable local knowledge index, policy/risk contracts, capability registry, guarded tool registry, functional deterministic Mosaic, initial agent loop and structured tracing.

## Milestones
- **0.1.1 Foundation:** reproducible package, runtime, Ollama, CI/quality gates.
- **0.2 Memory + Security:** SQLite/FTS, lifecycle/provenance, semantic retrieval, policy/permissions/audit.
- **0.3 Knowledge/RAG:** parsers, structural chunks, embeddings, hybrid retrieval, reranking, citations.
- **0.4 Mosaic + Capabilities:** intent/entities/domain/complexity/context/capability requirements and ExecutionPlan.
- **0.5 Tools + Policy:** filesystem/web/git/python/shell through policy, confirmation, sandbox, timeout and audit.
- **0.6 Agent Loop:** understand, retrieve, plan, execute, observe, evaluate, retry, respond.
- **0.7 Intelligent Router + Hardware POC:** capability routing plus safe ESP32 sensor/LED proof of concept.
- **0.8 Observability + Evals:** traces, metrics and memory/RAG/agent/tool/safety/offline evaluations.
- **0.9 Multimodal:** STT/TTS/voice/vision.
- **1.0 Personal AI:** useful offline end-to-end assistant with persistent memory, grounded knowledge, controlled actions and auditability.
- **1.1+ Hardware Gateway:** HAL/device discovery; Rust only where profiling/security/latency justify it.
- **2.0 Robotics:** embodiment with safety controller independent from the LLM.

## Engineering rules
1. Python-first; native only where necessary.
2. Modular monolith until operational evidence justifies extraction.
3. Models never grant their own permissions.
4. Hardware safety is enforced below the LLM.
5. Offline-first is tested, not merely documented.
6. Important actions are observable and auditable.
7. Evals decide whether a release actually improved.
8. Complexity must be earned.
