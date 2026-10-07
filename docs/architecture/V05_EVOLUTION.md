# Atlas 0.5 — Governed I/O Boundary

Atlas 0.5 closes the software boundary around external effects.

## Security
- deny-by-default permissions;
- scoped, expiring, single-use approval tokens;
- append-only hash-chained audit records with verification;
- central policy enforcement before tool execution.

## Tools
- manifest schemas and argument validation;
- duplicate registration protection;
- timeout/error lifecycle audit;
- explicit side-effect/idempotency metadata;
- shell-free subprocess execution for Git/Python tools.

## MCP
- transport protocol abstraction;
- initialize/discovery/call/close lifecycle;
- server health, disconnect and reconnect;
- adapter into Atlas ToolRegistry so MCP calls remain behind PolicyEngine.

## Hardware
- versioned `atlas-hw/1` messages with request IDs;
- HAL-style transport abstraction;
- heartbeat and reconnect;
- capability validation;
- SafetyController and emergency stop;
- deterministic ESP32 simulator.

The hardware software architecture is feature-complete for the current scope, but physical ESP32 validation remains a release gate before calling the physical hardware integration production-ready.
