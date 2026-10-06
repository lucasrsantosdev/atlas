# Atlas — 10/10 Target Matrix

`10/10` means complete for the Atlas 1.0 software scope: integrated, testable, observable and policy-governed. It does not mean perfect or production-certified.

## Implemented in 0.3.0-dev

- Integrated bounded Agent Loop: understand, retrieve, plan, execute, observe/evaluate, retry, respond.
- Mosaic `ExecutionPlan` with complexity, risk, context needs, capabilities and bounded execution.
- Local Memory lifecycle with active/superseded/forgotten states and ranked retrieval using lexical relevance, recency, confidence and importance.
- Knowledge hybrid retrieval combining lexical and deterministic local semantic hashing, with stable citations.
- Atlas core can receive a KnowledgeIndex and run the integrated AgentLoop.
- Policy-governed tool registry with explicit confirmation for high/critical risk.
- Trace metrics and per-stage spans.
- Transport-neutral MCP client contract with server/tool discovery, health and calls.
- Regression + evolution suite: 50 tests.

## Remaining gates before a literal 10/10 claim

- Replace deterministic semantic hashing with a production embedding provider and evaluate retrieval quality on a benchmark corpus.
- Add a real reranker and citation-faithfulness evaluation.
- Add real MCP transports/servers (stdio/HTTP as selected by the project), authentication, reconnect and policy adapters.
- Add OS process sandboxing and immutable/persistent audit sink for privileged tools.
- Add additional model providers, streaming, token budgets, circuit breakers and measured capability routing.
- Add end-to-end CI gates for coverage, typing, lint, offline and security evaluations.
- Hardware requires an actual gateway/device simulator first, then ESP32/device integration, heartbeat/fail-safe and independent safety controller.
- Multimodal and robotics remain post-1.0/explicit roadmap gates.

The project must not mark external integrations as complete merely because interfaces or mocks exist.
