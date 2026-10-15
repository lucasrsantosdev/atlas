# MOSAIC — CHAT 01 MASTER IMPLEMENTATION ROADMAP
**Version:** 1.0  
**Status:** Proposed execution plan for Chat 01  
**Date:** 2026-10-13  
**Authority:** MASTER / Architecture  
**Repository:** IGOR-SciDATA/mosaic, branch main

## 1. Purpose

This document consolidates the active Mosaic contracts into one logical, dependency-aware implementation sequence for Chat 01.

It does not replace the individual contracts. It tells Chat 01 which contract governs each decision, what to implement first, what must wait, and what evidence is required before moving on.

The goal is a complete, safe, user-friendly agentic workspace with a session-focused RAGNES context system, built by evolving the existing repository rather than rewriting it.

## 2. Contract registry and precedence

### 2.1 Active documents

1. **Mosaic MVP Implementation Contract v1.0** — original domain/database contract: entities, fields, nullability, defaults, foreign keys, allowed states, and the initial implementation sequence. Use the source document supplied in project/conversation context. Its repository path must be confirmed during Phase 0; do not assume a guessed path.
2. **MOSAIC_OFFICIAL_IMPLEMENTATION_CONTRACT_v1.1.md** — early implementation contract. Retained as historical context, but its narrower Harness roadmap is superseded where it conflicts with v1.2.
3. **MOSAIC_OFFICIAL_HARNESS_CONTRACT_v1.2.md** — authoritative target for complete Harness, execution loop, policy, tools, events, artifacts, API and Harness roadmap. It supersedes v1.1 for Harness scope and roadmap and selectively amends MVP v1.0.
4. **MOSAIC_FRONTEND_UX_IMPLEMENTATION_CONTRACT_v1.0.md** — authoritative user experience and React implementation contract.
5. **MOSAIC_RAGNES_CONTEXT_SYSTEM_CONTRACT_v1.0.md** — authoritative context retrieval, filtering, ranking, compaction, task/session continuity, artifact search and retrieval-evaluation contract.
6. **MOSAIC_REPOSITORY_AUDIT_2026-10-12.md** — static audit findings and known risks. Findings must be rechecked against the current branch; the audit is not proof of current runtime behavior.

### 2.2 Decision precedence

When requirements appear to conflict:

1. Safety and explicit MASTER decisions.
2. Harness v1.2 for Harness execution scope and lifecycle.
3. RAGNES v1.0 for context/retrieval/compaction behavior.
4. Frontend UX v1.0 for user-facing behavior.
5. MVP v1.0 for domain and database contracts except where an explicit later contract amends it.
6. Implementation contract v1.1 as historical context only where not superseded.
7. Current repository code as implementation truth, not as an excuse to preserve unsafe or incomplete behavior.

Do not silently resolve conflicts. Report the exact conflict, impact, and smallest proposed resolution. No speculative tables/fields or major infrastructure without an approved amendment.

## 3. Product target

Mosaic is an AI workspace, not merely a chat interface. The target end-to-end experience is:

User request → Conversation / Project → Task → RAGNES selects scoped context and relevant artifacts → Context Manager assembles bounded provider-neutral context → ModelProvider returns a structured decision → Harness validates policy and ToolCall → approval when required → constrained tool execution → persisted ToolResult and event → RAGNES updates task/session state and retrieves evidence as needed → validation → final response and artifacts → React displays result, timeline, approvals, and source references.

The Core owns state, policy, context assembly, execution, and persistence. The frontend displays and requests actions; it is not a security boundary.

## 4. Rules for every phase

Chat 01 must:
1. Read this roadmap and all applicable contracts.
2. Inspect the current branch before editing.
3. Identify the concrete gap and relevant existing modules.
4. Implement only the current phase.
5. Add focused tests before refactoring unrelated code.
6. Run tests/builds relevant to the change and report failures honestly.
7. Review the diff and API/schema compatibility.
8. Commit one coherent increment.
9. Report files changed, tests and commands run, results, limitations, and commit SHA.
10. Stop and wait for Master validation before starting the next phase.

Do not claim a feature works end-to-end based only on classes, endpoints, or unit tests existing. Demonstrate the real flow or mark it unverified.

## 5. Implementation sequence

Phases are sequential gates, not a request to implement the entire roadmap in one change. Some contracts have their own subphases; the master sequence below resolves their dependencies.

### Phase 0 — Repository baseline and contract reconciliation

**Goal:** establish the actual starting point.

Tasks:
- Inspect current branch, tree, commits, API routes, frontend components/API client, database initialization/migrations, and tests.
- Recheck findings in MOSAIC_REPOSITORY_AUDIT_2026-10-12.md.
- Find the exact repository location or confirm the external/project location of Mosaic MVP Implementation Contract v1.0.
- Reconcile schema discrepancies, especially Artifact/Setting versus database initialization and _mosaic_meta.
- Map Task, Action, ToolCall, ToolResult, Context Manager, Memory Manager, ModelProvider, Agent loop, workspace tools, and frontend routes to current contracts.
- Run existing backend tests, frontend tests/build, and lint/type checks if configured. Record unavailable dependencies or environment limitations; do not invent passing results.
- Produce a short baseline report and ordered list of concrete gaps.

**Exit gate:** Master approves baseline and any schema/API contract amendments. No feature implementation in this phase except minimal fixes required to obtain trustworthy baseline evidence.

### Phase 1 — Execution safety and authoritative state transitions

**Goal:** make execution safe and state changes coherent before exposing autonomous actions.

Tasks:
- Confine filesystem operations to the intended workspace; validate paths and symlinks and enforce file/output limits.
- Remove unsafe unrestricted shell execution. Define constrained command execution with timeout, cancellation, output limits, and required approval.
- Add input-schema validation for tool arguments and safe error/result handling.
- Establish one authoritative backend policy/approval decision point across Action and ToolCall lifecycles.
- Define and enforce legal Task/Action/ToolCall state transitions; reject invalid transitions.
- Ensure cancellation and duplicate requests are handled safely.
- Separate normalized public web search results from safe public-page fetch, and add/verify DNS/redirect/private-address/response-size protections for both.
- Ensure each registered tool declares a strict schema, scope, risk/side-effect class, approval policy, timeout, output limit and normalized result/error shape.
- Redact secrets and bound tool output.
- Do not add a permissions table or new database entities without an explicit approved schema amendment.

**Exit gate:** tests prove workspace confinement, filesystem create/read/write/list and overwrite semantics, unsafe command denial/approval, command timeout/cancellation, structured search results, safe source fetch/SSRF defenses, invalid transition rejection, bounded output, and approval state correctness.

### Phase 2 — Provider-backed Harness end-to-end

**Goal:** connect real model decisions to the execution loop.

Tasks:
- Implement or complete a provider-neutral structured decision protocol: final response versus tool request.
- Connect the real ModelProvider/Ollama implementation to the Harness loop.
- Persist user request, Task, tool intent, approval state, execution result, observations, and final result through existing repositories/contracts.
- Ensure ToolCall is intent and ToolResult is execution outcome.
- Ensure tool results become bounded observations for the next model call.
- Support iteration limits, cancellation, bounded retries/error recovery, and stopping conditions.
- Ensure approval-required actions pause and resume the same persisted Task after the decision; do not restart duplicate execution.
- Keep Harness as a service inside the existing Core, not a second Core.

**Exit gate:** integration test demonstrates a real provider-backed multi-step Task with tool call(s), persisted results, bounded observations fed back to the model, and a final response. The full suite also tests approval pause/resume, failure, iteration limit, cancellation, and a combined search → fetch → filesystem artifact → terminal validation workflow.

### Phase 3 — Execution events, Task APIs and reconnection substrate

**Goal:** make execution state observable and recoverable for the UI.

Tasks:
- Add the structured event service defined in Harness v1.2, with stable identity/order, timestamp, task/conversation/project/tool identifiers where applicable, status, duration, and redacted metadata.
- Persist or reliably replay canonical Task state and relevant events according to the approved persistence design.
- Implement/complete APIs to create/read/cancel Tasks, inspect status/plan, retrieve pending approvals and submit decisions, and retrieve results/artifacts where supported.
- Add SSE for task/execution events if required by the current API design; define reconnection and deduplication behavior.
- Treat persisted Core state as authoritative; events notify the UI but do not replace canonical state.
- Avoid a new event database table until reconciling Harness persistence requirements with current schema and confirming the minimal design.

**Exit gate:** API/integration tests prove task state retrieval, event ordering/deduplication, approval visibility, cancellation, and state recovery after simulated disconnect/reconnect.

### Phase 4 — RAGNES R0/R1: scoped context and safe artifact access

**Goal:** eliminate context pollution and let the agent consult files safely before advanced retrieval.

Tasks:
- Audit and fix Context Manager so it does not append unbounded tool results or indiscriminately include full history.
- Implement scopes: Core/global, project, conversation, Task/execution-session, and artifact/knowledge.
- Resolve current goal, subtask, constraints, acceptance criteria, and relevant project state before each model call.
- Build deterministic, bounded context assembly with source references and observable truncation/compaction metadata.
- Preserve explicit user constraints, applicable safety instructions, confirmed decisions, unresolved issues, and evidence.
- Implement workspace artifact inventory and bounded direct reads/excerpts with paths and line/range references where possible.
- Add safe discovery/loading of root-level `AGENTS.md` and, only if explicitly supported, a documented `AGENT.md` alias; handle nested files only for tasks scoped to their directory subtree.
- Separate project instruction files from Skills and ordinary knowledge documents; apply Core-policy precedence, bounded context inclusion, freshness checks, provenance, and explicit conflict reporting.
- Add tests for path/symlink escape, unrelated subtree instructions, conflicting instructions, stale content, prompt injection, and attempts to grant permissions from an instruction file.
- Enforce workspace boundaries, symlink/path checks, file-size limits, and output limits.
- Recheck source freshness before relying on files that may have changed.
- Do not introduce embeddings or a vector database in R0/R1.
- Do not create a Session table by default; use Conversation + Task + project/workspace unless a concrete gap is demonstrated.

**Exit gate:** tests prove context isolation, bounded history and tool observations, safe file access, explicit-file prioritization, source provenance, applicable `AGENTS.md` discovery/scope, conflict handling, freshness, and no cross-project/workspace leakage.

### Phase 5 — Frontend Task workspace and approval loop

**Goal:** make agentic mode understandable and controllable.

Tasks:
- Preserve Chat as default. A normal chat message must not automatically create an agentic Task.
- Add a task execution surface showing goal, friendly status, current/recent steps, and cancellation.
- Map backend Task statuses to friendly Portuguese labels; do not invent frontend-only authoritative states.
- Build a factual timeline from real persisted state/events, not simulated progress or fabricated percentages.
- Add an approval card describing action, target, impact, and choices actually supported by the Core.
- Connect approve/reject/cancel actions to real APIs and handle duplicate submissions.
- Add loading, error, empty, reconnecting, and mobile layouts.
- Keep technical details collapsed by default and never show hidden chain-of-thought.

**Exit gate:** frontend integration tests or documented manual end-to-end evidence show Task creation, status updates, approval pause/decision/resume, cancellation, and reconnect without duplicate execution.

### Phase 6 — RAGNES R2/R3: lexical retrieval and session compaction

**Goal:** retrieve relevant artifacts and resume long tasks without replaying the whole transcript.

Tasks:
- Add lexical search by path, filename, identifiers, symbols, and file content. SQLite FTS5 is an option, not a mandatory dependency; provide a justified fallback if needed.
- Rank explicit user-selected files, exact paths/identifiers, authoritative current contracts, and task-relevant evidence strongly.
- Return bounded excerpts with provenance instead of injecting large files wholesale.
- Implement versioned structured Task/session summaries using existing Task plan/result, project state, messages, ToolResults, and Artifacts where possible.
- Preserve objective, constraints, confirmed decisions, completed/verified work, relevant sources, open issues, pending approvals, and next step.
- Keep original sources; summaries are derived and must be invalidated/rechecked when sources change.
- Compact repetitive history and long tool output while preserving exit status, important failures, evidence, and references.
- Rebuild task/session state from persisted Core data on resume/restart.
- Coordinate any schema change with Master before adding fields/tables.

**Exit gate:** tests prove relevant file retrieval, correct source references, preservation of explicit constraints, stale-summary handling, and continuation after restart/resume.

### Phase 7 — Retrieval evaluation and frontend source transparency

**Goal:** measure quality before heavier retrieval and show users where results came from.

Tasks:
- Build a fixed evaluation set with known relevant files/facts, constraints, and expected outcomes.
- Measure retrieval recall, irrelevant/duplicate context ratio, source correctness, constraint preservation, task/answer success, latency, and budget compliance.
- Compare baseline context behavior with RAGNES R0-R3.
- Add “Fontes consultadas / Contexto usado” in task results, showing actual source files/references.
- Add expandable diagnostics for retrieval type, selected sources, truncation/compaction, and approximate budget usage when available.
- Do not present internal ranking scores as certainty and do not fabricate token counts.

**Exit gate:** baseline and RAGNES results are recorded; Master reviews whether retrieval quality justifies the next phase.

### Phase 8 — Skills and explicit context/resource budgets

**Goal:** reuse procedures and keep execution bounded without confusing skill selection with permission.

Tasks:
- Implement Skills as versioned reusable procedures with scope, description, inputs, and instructions, following Harness v1.2.
- Integrate the project-instruction loader into context selection and task traces; expose the instruction files applied and their scope in the source inspector.
- Keep the user experience clear about adding instruction files versus adding Skills; neither mechanism grants tool permissions.
- Select only task-relevant Skills and include them within RAGNES context budget.
- Skills do not grant permission; Core policy remains authoritative.
- Define model/context budget behavior, output reservation, iteration/time limits, and how low-ranked context is removed first.
- Expose execution profiles in frontend only when corresponding backend policy is implemented and enforced.
- Preserve user control over enabled Skills and relevant settings.

**Exit gate:** tests prove relevant Skill selection, versioning, budget enforcement, and that Skills cannot bypass policy/approval.

### Phase 9 — Results, artifacts and observability UX completion

**Goal:** complete the end-user lifecycle.

Tasks:
- Display concise final summary, validation outcomes, limitations, and generated artifacts.
- Support safe open/download actions using real artifact APIs.
- Preserve task history and execution timeline after completion.
- Add filtered technical details for events, ToolCalls, ToolResults, durations, errors, and source references.
- Redact secrets and keep technical details collapsed by default.
- Complete keyboard accessibility, screen-reader status announcements, reduced motion, and responsive layouts.
- Only expose settings and controls the backend actually supports.

**Exit gate:** user can start a Task, follow progress, approve gated actions, cancel, inspect sources, and open final artifacts through the real frontend/Core flow.

### Phase 10 — Conditional embeddings/hybrid retrieval

**Goal:** address demonstrated lexical-retrieval gaps, not add complexity preemptively.

Only proceed if Phase 7 evaluation identifies material retrieval failures that lexical search cannot adequately solve.

Tasks:
- Compare local embedding options suitable for target hardware.
- Introduce an adapter/index as derived, rebuildable data without replacing original files or lexical search.
- Evaluate hybrid retrieval and optionally reranking against the same fixed test set.
- Record quality gain, latency, RAM/CPU use, maintenance burden, and failure modes.
- Keep embeddings/vector index optional and recoverable.

**Exit gate:** measurable quality gain justifies complexity and resource cost; otherwise document the decision to defer.

### Phase 11 — Full acceptance, regression and runbook

**Goal:** validate the whole product and prepare a repeatable development workflow.

Required scenarios:
- root-level and applicable nested `AGENTS.md` discovery, bounded inclusion, provenance, freshness and conflicts;
- project instruction prompt injection and attempts to bypass Core policy are rejected/ignored as authority;
- normal chat remains normal chat;
- provider-backed multi-step Task with real tool calls;
- filesystem list/read/create/write within workspace, with overwrite, traversal and symlink protections;
- terminal command execution with non-zero exit, timeout, cancellation and output-limit handling;
- structured web search and source-preserving public-page fetch with SSRF/redirect protections;
- combined search → fetch → write artifact → run validation → grounded final response;
- unsafe tool request rejected or gated;
- approval pause/decision/resume;
- cancellation and failure recovery;
- bounded context with many irrelevant files;
- retrieval with traceable sources;
- compaction preserving user constraints and decisions;
- task resume after restart/reconnect;
- stale or contradictory sources;
- prompt injection embedded in retrieved files;
- result/artifact display;
- no cross-project/workspace leakage;
- responsive and accessible frontend;
- configured backend/frontend tests and builds.

Deliver a runbook covering setup, tests, provider prerequisites, workspace boundaries, recovery, known limitations, and how to inspect execution logs.

**Exit gate:** all mandatory tests pass or each exception is explicitly documented and approved; Master validates the final diff and declares the milestone.

## 6. Dependency map

- Phase 0 precedes all implementation.
- Phase 1 precedes real tool execution.
- Phase 2 depends on Phase 1.
- Phase 3 depends on the execution lifecycle from Phase 2. Event design can be drafted earlier, but final wiring must use canonical state.
- Phase 4 can begin after Phase 0 and must respect Phase 1 safety boundaries; complete it before broad autonomous artifact exploration.
- Phase 5 depends on stable Task/approval APIs and event/reconnect behavior from Phase 3.
- Phase 6 builds on Phase 4.
- Phase 7 evaluates Phase 4 and Phase 6 and adds source transparency to UI.
- Phase 8 depends on RAGNES budgets and Harness policy.
- Phase 9 completes UI capabilities on stable APIs/events/artifacts.
- Phase 10 is conditional on Phase 7 results.
- Phase 11 validates the integrated system.

Do not run duplicate independent Harness RAG and RAGNES implementations. RAGNES is the single context/retrieval/compaction system integrated with Harness.

## 7. What not to build without a new decision

- A second Core or a second Harness.
- A second task/session state system in React.
- A Session table before a demonstrated need.
- Mandatory vector database or embeddings before evaluation.
- Multi-agent orchestration.
- Distributed queues/workers, Redis, Kafka, Kubernetes, or microservices.
- Multi-user authentication/authorization infrastructure outside approved single-user MVP.
- Unrestricted shell or arbitrary filesystem access.
- Frontend-only permissions or fake approval/progress states.
- Speculative database fields/tables.
- A Skills marketplace or browser automation unless separately approved.

## 8. Definition of the first practical milestone

The first practical milestone is not the entire roadmap. It is:

1. Safe, authoritative Task/Action/ToolCall state transitions.
2. Real provider-backed Harness loop with one verified tool-observation-final cycle.
3. Recoverable task APIs/events sufficient for frontend integration.
4. RAGNES R0/R1: bounded, scoped context and safe, traceable artifact reads.
5. Frontend Task status/timeline and real approval loop.
6. Focused tests proving these paths end-to-end.

After that milestone is validated, proceed to lexical retrieval, session compaction, evaluation, Skills, richer UI, and only then conditional embeddings.

## 9. Final instruction to Chat 01

**Implement only the next uncompleted phase.** The repository audit is historical evidence; recheck current code and run relevant tests. Do not treat target architecture as proof that a feature already exists. Do not skip phases because a module name or unit test exists. If a contract conflict or schema/API gap is discovered, stop, report it, and wait for Master decision before making an architectural change.
