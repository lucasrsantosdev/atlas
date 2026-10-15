# MOSAIC — REPOSITORY AUDIT

**Date:** 2026-10-12  
**Repository:** https://github.com/IGOR-SciDATA/mosaic  
**Branch:** main  
**Method:** static review of the repository tree, database initialization, core services, API modules, provider, tools, frontend API/UI entry points and selected tests.

> **Scope limitation:** This is a code-reading audit of the GitHub branch. I did not execute the repository in a clean runtime, run its tests, install dependencies, or exercise a real Ollama instance in this audit. Therefore test coverage found in the tree is not reported as passing.

## Executive verdict

Mosaic has a meaningful single-process MVP foundation and should be extended, not rebuilt. The strongest current pieces are SQLite persistence, a deterministic context builder, Ollama adapter, REST/SSE chat, project-scoped context isolation tests, and a bounded callable agent loop.

The principal gap is integration and operational safety: the existing agent loop receives a callback named `decide` rather than directly proving provider-backed tool selection; approval-required calls can pause, but a complete persisted approval/resume path is not established by the reviewed files; and the available filesystem/terminal tools are not safely confined to project workspaces. There is also no observed event/logging service or observability console in the current file tree.

## Confirmed repository structure

Backend includes:
- `backend/app/api/`: actions, chat, conversations, memories, messages, models, projects, tasks.
- `backend/app/context/manager.py`, `backend/app/memory/manager.py`.
- SQLite database and repositories for actions, conversations, memories, messages, projects, tasks, tool calls and tool results.
- `backend/app/providers/ollama.py` and provider base abstraction.
- `backend/app/services/agent.py`, `chat.py`, `project.py`, `tools.py`.
- Built-in filesystem, terminal, calculator, search and weather tools.
- Backend tests for model, conversation, message, memory, project, task, action, provider, chat, context isolation, tools and agent.
Frontend includes a React/Vite app, API wrapper and stylesheet. The frontend package scripts show dev/build/preview, but no test script was found in `frontend/package.json`.

## Findings by priority

### P0 — Must address before exposing agent execution

**1. Filesystem tool is not workspace-confined.**  
`backend/app/tools/builtin.py` constructs `Path(arguments["path"])` and reads/writes/lists it without checking that the resolved path remains inside the active project workspace. A model-proposed or user-supplied path can target locations outside the project. Add workspace-root resolution, traversal rejection, symlink escape checks and tests.

**2. Terminal tool executes an arbitrary shell string.**  
The current implementation uses `subprocess.run(command, shell=True, timeout=30)`. Approval metadata is present, but this alone is not a sandbox. Before agent execution is enabled, execution must be scoped to the project workspace, have process cleanup, output limits and a backend-enforced approval policy. Document the remaining OS-level security boundary honestly.

**3. Tool schema validation is partial.**  
`Tool.validate` checks required fields and some primitive types, but does not generally reject unknown properties, validate enum/range constraints, or enforce the complete schema. Fail closed for unsupported schema features and validate tool-specific operations.

**4. Network tools have minimal controls.**  
Search and weather use `urlopen` with timeouts, but the reviewed code does not establish response-size limits, redirect destination checks, or a reusable safe-fetch policy. Add bounded requests and safe destination validation before generalizing web fetch.

### P1 — Harness not yet proven end-to-end

**5. Agent loop is not shown wired to the actual model provider.**  
`run_agent(task_id, decide, ...)` accepts an injected decision callback. It can process `tool_call` and `final` decisions, persists tool calls/results and enforces an iteration limit. The reviewed code does not show a provider adapter translating real model responses into validated decisions, nor an API/UI entry point that runs the whole task end to end. Implement this using the existing ModelProvider and Task; do not create a new Core.

**6. Approval pause/resume is incomplete in the reviewed path.**  
For an approval-required tool, the loop changes Task to `awaiting_approval` and returns the ToolCall ID. The reviewed code does not establish that approving the persisted ToolCall resumes the same run and continues the model loop. Approval and execution must resume the same task/call without duplicate side effects.

**7. Action and ToolCall lifecycle are separate and can drift.**  
The repository has an Action transition service and a ToolCall execution service. The reviewed execution service validates/approves/executes ToolCall but does not use the Action lifecycle as a shared policy decision point. Keep both domain concepts, but centralize the server-side policy decision and test consistency. Do not add a permissions table.

**8. Task API permits direct status updates.**  
`PATCH /tasks/{task_id}` accepts a status and forwards it to repository validation; allowed values are checked, but a legal transition graph is not enforced there. Enforce lifecycle transitions in the service/repository, not only in agent control flow.

### P1 — Observability gap

**9. No structured execution event service or console was found in the inspected tree.**  
The current code persists Task, ToolCall and ToolResult, which are useful sources for a timeline, but there is no dedicated correlated event stream/logging service visible in the tree and no UI section for live task traces, filtered logs or approval inbox. Add structured local events with task/conversation/project/tool_call IDs, timestamps, durations, statuses and redaction. Start with local logs; do not introduce a message broker or external logging platform.

### P2 — Contract and persistence discrepancies

**10. Database schema differs from the declared entity contract.**  
`backend/app/db/database.py` creates `_mosaic_meta`, but the reviewed initialization code does not create the contract-listed `artifacts` or `settings` tables. This is a contract discrepancy, not automatic permission to add or delete tables. Master must explicitly decide whether those entities are in the immediate scope or deferred.

**11. Conversation mode contract should be enforced.**  
The contract defines MVP conversation mode as `chat`, but current schema stores mode as TEXT with default `chat` and no database CHECK constraint. Keep the domain/API validation aligned with the contract; do not invent new conversation modes to represent agent tasks.

**12. Tool results are available to context, but context size should be bounded.**  
`build_context` bounds recent conversation history to 20 messages, but appends tool results from all stored calls in the conversation. Add a bounded/relevant selection policy so long sessions do not grow without limit. Preserve source IDs and status in the operational timeline.

**13. Frontend API does not expose Tasks/Actions/ToolCalls for a usable execution workflow.**  
The inspected `frontend/src/api.js` exposes models, projects, conversations and memories, but not tasks, actions, tool calls, event logs or approval actions. This confirms the UI cannot yet offer a complete observability/approval workflow through that wrapper.

## Positive evidence worth preserving

- SQLite connections enable `PRAGMA foreign_keys = ON`.
- Model uniqueness is enforced with a unique index on `provider, model_name`.
- Context Manager includes identity, bounded recent history, project state, memories and task/tool observations.
- A project/conversation isolation test explicitly verifies that one project's state/memory and another conversation's history do not leak into each other.
- Ollama is behind a provider abstraction and handles generation/streaming.
- Agent loop has a configurable positive iteration limit and tests for tool→observation→final, approval-required pause, limit and cancellation.
- The current architecture already has the right broad components; the key work is safe integration and validation.

## Recommended order

1. Baseline: run backend tests and frontend production build in a clean environment; record actual results.
2. Fix tool safety and complete validation/transition enforcement.
3. Wire the existing agent loop to the real ModelProvider with validated decisions and approval resume.
4. Add correlated structured execution events.
5. Add K0/K1 document access and lexical retrieval; no embeddings/vector DB until measured need.
6. Add observability and approval UI to the existing frontend.
7. Run end-to-end tests and publish a local runbook.

## Acceptance evidence still required

- Exact backend test command and pass/fail output.
- Frontend `npm run build` output.
- Fake-provider end-to-end test for tool call → approval → execution → observation → final answer.
- Security tests for workspace traversal/symlink escape, shell restrictions, timeouts, output limits and denied tools.
- Cancellation/failure/restart tests.
- Project and conversation isolation tests.
- Correlated event timeline for a complete task.
- Documentation updated to match actual implementation.

## Audit status

**Static audit complete; runtime verification pending.** The official next-stage contract is `docs/MOSAIC_OFFICIAL_IMPLEMENTATION_CONTRACT_v1.1.md`.
