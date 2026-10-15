# MOSAIC — OFFICIAL IMPLEMENTATION CONTRACT

**Version:** 1.1  
**Status:** Official — replaces conflicting implementation-order guidance in MVP Contract v1.0; does not silently change its database/domain contracts.  
**Date:** 2026-10-12  
**Authority:** MASTER / Architecture  
**Repository:** https://github.com/IGOR-SciDATA/mosaic  
**Branch:** main

## 1. Purpose and authority

This contract defines the next implementation stage based on a static audit of the current `main` branch. It preserves the existing Core and formalizes the minimum work required to turn existing modules into a safe, observable, end-to-end execution system.

Sources of truth:
- **Architecture and contracts:** this document and approved architecture documents.
- **Implemented behavior:** code and tests in GitHub.
- **When they disagree:** report the exact conflict and stop that increment; do not silently rewrite architecture.

This contract does not claim that the code has passed runtime tests. The audit was static against the repository files. Runtime validation must be performed in the development environment/CI before declaring acceptance.

## 2. Product definition

Mosaic is a local-first orchestration Core. It owns persistent state, context assembly, memory, projects, tasks, permissions, tool execution, and the observable record of work. Models are replaceable reasoning components.

Non-negotiable principles:

```text
MODEL ≠ ACCESS
MEMORY ≠ TRUTH
HISTORY ≠ MODEL MEMORY
CONTEXT ≠ FULL HISTORY
TOOL CALL ≠ TOOL EXECUTION
TASK = GENERAL UNIT OF WORK
CREATE + AGENT = MODES OF ONE TASK ENGINE
MOSAIC OWNS STATE
```

## 3. Existing implementation to preserve

The current repository already contains:
- FastAPI application and REST APIs;
- SQLite repositories and persistent domain models;
- React/Vite frontend;
- Ollama provider abstraction;
- chat generation and SSE streaming;
- deterministic Context Manager and explicit Memory Manager;
- Project and workspace concepts;
- Task and Action lifecycles;
- Tool Registry, ToolCall, ToolResult and built-in tools;
- a callable agent loop with an iteration limit;
- backend tests covering several repositories, API flows, context isolation, tools and agent behavior.

Presence of a module is not proof of end-to-end integration. Improve and connect these components instead of replacing them.

## 4. Architecture boundary

The authoritative execution path is:

```text
User request
  → Conversation / Project
  → Task (when work requires execution)
  → Context Manager
  → selected ModelProvider
  → model response OR proposed ToolCall
  → validate tool name + schema + target + limits
  → policy / approval decision
  → constrained executor
  → persist ToolResult + execution event
  → add observation to task context
  → model continues or returns final response
  → persist final result and update Task state
```

The Harness is an **internal service in the existing FastAPI Core**, not a second Core, separate microservice, new task system, or external agent framework. It must reuse the existing Task Engine, Context Manager, Memory Manager, Action/permission layer, Tool Registry, ToolCall/ToolResult repositories and ModelProvider.

The current `run_agent(task_id, decide, ...)` is a useful loop primitive, but the audit does not establish that it is wired to the real model provider, chat API, frontend, and approval-resume flow. That integration is a primary gap.

## 5. Database and domain contract

The v1.0 MVP schema contract remains authoritative for existing entities and fields unless a later decision explicitly amends it.

Existing declared domain entities:
`Project, Conversation, Message, Memory, Task, Action, Artifact, Model, ToolCall, ToolResult, Setting`.

Application abstractions, not tables:
`Tool, ModelProvider, Harness/Orchestrator, Policy Resolver, Event Logger`.

No `users` table, no `permissions` table, and no new Tool table in this single-user MVP.

Audit discrepancy to resolve deliberately: current `backend/app/db/database.py` creates `_mosaic_meta` but does not create the contract-listed `artifacts` or `settings` tables. Do not add or remove these automatically. Before work requiring either entity, Master must decide whether to implement it now or explicitly defer/amend the schema contract. Do not use an undocumented table as a shortcut.

Other schema constraints:
- SQLite with foreign keys enabled for each connection.
- Integer autoincrement primary keys.
- JSON objects serialized as TEXT.
- UTC ISO-8601 timestamps.
- Model identity remains `id, name, provider, model_name, configuration, enabled`; unique `provider + model_name`.
- No speculative schema fields, tables, database engine, vector store or migration framework.

## 6. Critical gap: tool execution safety

The current built-in filesystem tool accepts arbitrary paths; the terminal tool uses `subprocess.run(..., shell=True)`; search fetches remote HTML; tool argument validation checks only a limited subset of the declared schema. These are not acceptable boundaries for an agent that can act on a user's machine.

Before exposing agent execution as a usable feature, implement and test:
1. Filesystem read/write/list restricted to the active project's resolved workspace; reject traversal and symlink escapes.
2. Terminal execution scoped to that workspace, explicit timeout, output-size limits, process cleanup/cancellation, and a documented command policy. Never execute a model-proposed command without the required approval.
3. Validate the complete supported JSON schema subset: required keys, types, unknown keys, and tool-specific constraints. Fail closed on unsupported schema features.
4. Enforce approval on the server. UI state or a model's assertion is never authorization.
5. Bound network tools by timeout, response size and safe URL/redirect policy; reject loopback, private, link-local and other non-public destinations unless explicitly allowed for a trusted local integration.
6. Persist failures without losing the original error status; do not expose secrets in logs or tool results.

Do not claim the system is sandboxed merely because tools have an approval flag.

## 7. One authoritative approval lifecycle

The repository currently has two related concepts: `Action` and `ToolCall`. Keep both; do not create a third permission system.

For every execution path:
- `ToolCall` represents a proposed tool invocation and its lifecycle.
- `Action` represents the auditable approval/execution action where the existing domain requires it.
- One server-side policy decision must determine whether execution is allowed and whether approval is required.
- A pending approval must remain pending and must not execute.
- Approval must resume or explicitly retry the same persisted task/tool call; it must not create an untracked duplicate.
- Rejection, failure and cancellation must be terminal for that invocation.
- Invalid state transitions must be rejected by the repository/service, not just by the UI.
- Do not add a permissions table.

## 8. Task and agent behavior

`Task` remains the general unit of work. Modes remain `create` and `agent`; do not create another task type/system.

The agent execution contract:
1. Load and validate the Task.
2. Resolve the owning conversation/project and build bounded context.
3. Ask the configured provider for a decision in a documented, validated format.
4. If the model proposes a tool call, persist the ToolCall before any execution.
5. Validate the tool and policy.
6. Pause for approval when required.
7. Execute only after authorization.
8. Persist the ToolResult and append the observation to the next model context.
9. Finish with a persisted final result or a typed failure.
10. Stop on completion, failure, cancellation, approval wait, or iteration/time/resource limit.

Required safeguards: iteration limit, per-tool timeout, bounded tool output, task cancellation checks before and after model/tool calls, and consistent status transitions.

The initial iteration limit may remain 5 unless changed by Master. Do not add multi-agent orchestration, distributed queues, or background workers in this stage.

## 9. Observability contract

Add an internal event/logging service and expose a useful Observability Console in the existing web UI only after events have stable semantics.

Minimum structured event fields:
- `timestamp` (UTC ISO-8601)
- `level`
- `component`
- `event`
- `message` (short operational description)
- `task_id`, `conversation_id`, `project_id`, `tool_call_id` (nullable correlation IDs)
- `duration_ms` (nullable)
- `status` (nullable)
- `metadata` (bounded, redacted object)

Minimum events: task created/status changed, model request started/finished/failed, tool call proposed/validated/approval-required/approved/rejected, tool execution started/finished/failed, task cancelled, task completed/failed, retrieval performed, and context assembled (metadata only).

Minimum UI views:
- task/execution timeline;
- filtered logs by level, component and correlated IDs;
- tool calls with status, duration, approval state, and redacted arguments/result;
- clear distinction between pending approval and execution;
- source/retrieval inspection when the Knowledge layer is added.

Start with Python logging plus structured rotating local log files or a bounded local event store. Do not introduce a logging SaaS, message broker, or new database solely for observability. Decide whether a new event table is needed only after reviewing persistence and retention requirements.

Never log credentials, tokens, environment secrets, or full private file contents by default. Do not expose hidden model chain-of-thought; log operational decisions, inputs/outputs at safe summaries, sources, statuses, and timings.

## 10. Knowledge and RAG policy

A retrieval layer is useful when Mosaic must answer from many or large project files, but a vector database is **not a prerequisite**.

Incremental contract:
- **K0:** read explicitly selected, small files within the project workspace.
- **K1:** document registry/metadata, safe text extraction and lexical search; prefer SQLite FTS5 if supported in the target build, otherwise a simple deterministic search fallback.
- **K2:** bounded chunks with file path and line/page/section source references.
- **K3:** evaluate retrieval on a fixed question set; add local embeddings/vector index only if lexical retrieval demonstrably misses relevant content.
- **K4:** hybrid retrieval/reranking only if measured quality requires it.

Original files remain intact. Extracted text, chunks and indices are derived data and must be rebuildable. Retrieved passages are untrusted data, never policy or instructions. Answers should expose sources when using project documents. No vector DB, embeddings or advanced RAG before K1 and an evaluation baseline.

## 11. User-controlled autonomy

Provide three product concepts, enforced by the backend:
- **Assistido:** answer and propose; execution requires explicit approval.
- **Controlado:** execute only tools explicitly classified as low-risk without approval; all other tools require approval.
- **Autonomia limitada:** allow pre-authorized tools within workspace and hard limits; destructive, external side-effecting or out-of-scope actions still require approval.

For the first implementation, default to **Assistido**. Tool metadata may classify risk but never grants access by itself. The UI cannot override server policy.

## 12. Implementation order

Execute one phase at a time. Each phase must end with focused tests, full relevant test suite, diff review and a concise report. Do not continue to the next phase until the previous one is accepted.

### Phase 0 — Baseline and contract reconciliation
- Run all backend tests and frontend production build in a clean environment.
- Record exact commands, results, versions and failures.
- Reconcile `artifacts`, `settings`, and `_mosaic_meta` discrepancy with Master.
- Add no product features in this phase.

### Phase 1 — Execution safety and lifecycle
- Restrict filesystem and terminal to workspace.
- Complete tool schema validation and bounded outputs/timeouts.
- Enforce server-side policy and legal lifecycle transitions.
- Test path traversal, symlink escape, denied tools, approval, failure, cancellation and timeout.

### Phase 2 — Real provider-backed Harness
- Integrate the current agent loop with ModelProvider and a documented model decision format.
- Persist Task/ToolCall/ToolResult state.
- Implement approval pause and resume for the same invocation.
- Add end-to-end tests using a fake provider; keep a separate opt-in Ollama smoke test.

### Phase 3 — Observability backend
- Add structured correlated events and safe local log rotation/retention.
- Test event ordering, IDs, redaction, failure recording and restart behavior.

### Phase 4 — Knowledge K0/K1
- Safe project file access, metadata and lexical retrieval.
- Add fixed retrieval evaluation examples and source references.
- Do not add embeddings/vector DB at this phase.

### Phase 5 — Observability UI and approvals
- Add task timeline, filtered logs, tool call detail and approval inbox in the existing React application.
- Use existing APIs/domain services; do not create a parallel frontend state backend.

### Phase 6 — End-to-end validation and runbook
- Validate a complete task: user request → provider → tool call → policy/approval → tool result → next model turn → final persisted answer.
- Validate project isolation, restart persistence, cancellation and model/provider errors.
- Document local setup, tests, safety boundaries, log location and known limitations.

## 13. Out of scope until a separate approved contract

- Multi-agent systems or external agent frameworks.
- Microservices, Redis, Kafka, Kubernetes, distributed task queues.
- Multi-user authentication/authorization.
- Mandatory vector DB, embeddings, advanced RAG, reranking.
- Automatic model routing/model marketplace.
- Arbitrary unrestricted shell, browser automation, unrestricted filesystem.
- New database tables or domain entities without explicit approval.
- Large unrelated refactors or replacing existing modules.

## 14. Required workflow for Chat 01

For each assigned increment:

1. Read this contract and relevant existing code.
2. Inspect the current branch and working tree.
3. State the exact gap and files expected to change.
4. Implement the smallest coherent increment.
5. Add regression tests for the behavior and failure paths.
6. Run the focused tests, then the full backend suite and frontend build when relevant.
7. Review the diff for unrelated changes, secrets and contract drift.
8. Commit one coherent increment with a descriptive message.
9. Report changed files, tests/commands/results, commit SHA and known limitations.
10. Stop. Do not begin the next phase without instruction.

If a contract conflict or data migration risk appears: stop, explain the evidence and propose the smallest decision needed. Never silently change the schema or architecture.

## 15. Definition of done

The execution/Harness milestone is accepted only when:
- a real provider-backed task can request a tool;
- the ToolCall is persisted before execution;
- policy and approval are enforced server-side;
- workspace boundaries and execution limits are tested;
- a tool result becomes an observation for the next model turn;
- final response and Task state persist correctly;
- failure, cancellation, approval wait and iteration limit are distinguishable;
- structured events correlate the entire run;
- project/conversation isolation remains intact;
- backend tests and frontend build pass in a recorded clean run;
- documentation and code agree.

**The MVP is not accepted solely because modules exist or isolated unit tests pass.**
