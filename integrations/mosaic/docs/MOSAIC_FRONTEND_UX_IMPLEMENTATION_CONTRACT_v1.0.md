# MOSAIC — FRONTEND UX & IMPLEMENTATION CONTRACT
**Version:** 1.0  
**Status:** Proposed official frontend contract  
**Date:** 2026-10-12  
**Authority:** MASTER / Architecture  
**Depends on:** MOSAIC_OFFICIAL_HARNESS_CONTRACT_v1.2.md, Mosaic_MVP_Implementation_Contract.md

---

## 1. Purpose

Define how Mosaic presents agentic execution in a friendly, understandable, inspectable, and user-controlled interface.

The frontend is not merely a chat screen and must not become a technical dashboard that overwhelms normal users. It is an **AI workspace**: conversation remains the main entry point, while complex work gains a visible task view, approvals, artifacts, and an execution timeline.

This contract defines target behavior and UX. It does not require implementing every screen in one commit. Implementation must follow the phased roadmap and inspect the current repository before changing it.

## 2. Product experience

The user should understand, at all times:

1. What Mosaic understood as the goal.
2. Whether Mosaic is answering or executing a task.
3. What has happened and what is happening now.
4. Whether Mosaic is waiting for the user.
5. What resources or actions need approval.
6. What was produced, where it was saved, and what failed.
7. How to stop execution and inspect details.

The user should not need to understand Harness, ToolCall, Context Manager, provider protocols, or database entities to use the product.

**UX rule:** expose the outcome and meaningful progress by default; expose technical details on demand.

## 3. Non-negotiable principles

- React presents state; the Core owns policy, execution, persistence, and authoritative task state.
- A frontend control is never an authorization boundary.
- Chat remains the default entry point. Do not force users to configure an agent before asking a question.
- A Task is the unit of structured work. Do not create a second frontend-only task system.
- The UI must distinguish a proposed action from an executed action.
- Approval requests must state the operation, target, consequence, and available choices.
- Never show fabricated progress. Progress labels must be derived from persisted state/events.
- A disconnected stream must not be interpreted as task completion or failure.
- Keep technical logs collapsed by default; never expose hidden chain-of-thought. Show concise plans, actions, observations, source references, and results.
- Prefer a small number of clear screens over many disconnected configuration pages.
- UI language is Brazilian Portuguese initially, with user-friendly labels rather than internal class/entity names.

## 4. Information architecture

### 4.1 Primary workspace

**A. Sidebar**
- New conversation
- Conversation history
- Projects
- Settings
- Collapsible on narrow screens

**B. Main conversation**
- Message history
- Composer
- Model selector using real enabled Models returned by the Core
- Current project/context indicator when relevant
- Mode selector or action affordance for Chat / Agent, without making it mandatory for simple chat
- Attach/select files where supported, including project instruction files when the backend supports them
- Streaming assistant response

**C. Task execution surface**
- Appears when the conversation has an active or selected Task
- May be a panel beside the chat on wide screens or a dedicated drawer/tab on small screens
- Shows goal, friendly status, current step, recent completed steps, approval requests, output artifacts, and a details expander
- Must not permanently consume the main chat area when no task is active

### 4.2 Supporting views

- **Task history:** tasks belonging to the selected project/conversation, with status and result.
- **Approval inbox:** pending decisions requiring user input.
- **Artifacts:** files/results produced by tasks, with safe open/download actions.
- **Execution details:** filtered events, tool calls, results, errors, durations and source references.
- **Settings:** execution profile, default model, and relevant tool/skill controls as they become available.
- **Project instructions:** show discovered/applicable instruction files (such as `AGENTS.md`), allow users to add/select them only through real backend-supported flows, and show the scope in which they apply.

Do not implement all supporting views before the end-to-end task flow works.

## 5. Chat and Agent experience

### 5.1 Chat is the default

A normal question should remain a normal conversation. The UI must not create an agent task merely because the user sent a message.

### 5.2 Agent mode

Agent mode means: Mosaic can carry out a bounded task through multiple validated steps, using available tools and returning observations to the model.

Recommended user-facing label: **Executar tarefa** or **Modo agente**. Prefer “Executar tarefa” in primary actions and reserve “Modo agente” for settings/help where useful.

The user can:
- describe the goal in natural language;
- optionally choose a project or files;
- select an execution profile;
- start the task;
- inspect progress;
- approve or reject gated operations;
- cancel execution;
- review the final result and artifacts.

The frontend must not promise unrestricted autonomy. Tool availability, workspace boundaries, approvals, and budgets are enforced by the Core.

### 5.3 Task confirmation

For an ambiguous or potentially costly task, Mosaic may show a concise goal summary and plan before execution. Do not require confirmation for every harmless step.

Example:
> **Vou organizar os arquivos deste projeto.**  
> 1. Verificar os arquivos disponíveis  
> 2. Identificar duplicados e tipos  
> 3. Propor uma organização  
>  
> [Revisar plano] [Iniciar tarefa]

The plan is a user-facing summary, not hidden chain-of-thought. If the task can safely begin without clarification, avoid unnecessary friction.

## 6. Execution timeline

Every task view should provide a readable timeline. Example:

- **Tarefa criada** — objetivo registrado.
- **Analisando o projeto** — Mosaic está verificando o contexto necessário.
- **Consultando arquivos** — leitura de arquivos autorizados.
- **Aguardando sua aprovação** — uma ação requer autorização.
- **Executando ação aprovada** — operação iniciada.
- **Validando resultado** — verificando se o objetivo foi atendido.
- **Concluída** — resultado e artefatos disponíveis.

Each item may include timestamp and a short description. Tool-specific technical data, safe arguments and bounded outputs are behind “Ver detalhes”. The UI must distinguish a proposed tool call from an executed operation and show the authoritative Core result.

### 6.1 Status mapping

Map persisted Task statuses to friendly labels; do not create alternative frontend state as the source of truth.

| Core status | User-facing label | Suggested presentation |
|---|---|---|
| pending | Na fila | Neutral |
| planning | Preparando a tarefa | In progress |
| awaiting_approval | Preciso da sua aprovação | Attention required |
| executing | Executando | In progress |
| validating | Conferindo o resultado | In progress |
| completed | Concluída | Success |
| failed | Não foi possível concluir | Error with next steps |
| cancelled | Tarefa cancelada | Neutral |

Status colours/icons are supplementary; always include text. Unknown future states must render safely as “Status atualizado” with details available.

### 6.2 Progress indicator

Do not display a percentage unless the backend supplies a defensible progress measure. Otherwise show:
- current step;
- completed step count, if known;
- elapsed time when reliably measured;
- a non-numeric activity indicator.

Do not infer “80% complete” from iteration count.

## 7. Approval experience

Approval is a first-class interaction, not a browser confirmation dialog.

An approval card must show:
- **What Mosaic wants to do** in plain language, naming the capability (for example, read/write a project file, run a command, search the web or fetch a page).
- Target path/resource or external destination.
- Relevant arguments/impact, safely formatted.
- Why approval is required.
- Whether the action reads or writes files, may overwrite content, executes a process/command, accesses the network, or changes external state.
- Choices supported by the Core: approve, reject, or cancel the task when available.

Example:
> **Permitir executar os testes do projeto?**  
> Mosaic pretende executar pytest dentro do workspace deste projeto. Isso iniciará um processo local e poderá consumir recursos da máquina.  
>  
> [Permitir desta vez] [Recusar] [Ver detalhes]

Buttons must reflect actual backend capabilities. Do not offer “always allow” unless a real, persisted, revocable policy exists and the Core enforces it.

After a decision, show the authoritative result from the Core. Disable duplicate submissions while a request is in flight and make retries safe.

## 8. Execution profiles

Expose a small number of understandable profiles, with descriptions and a visible current selection:

- **Assistido:** Mosaic proposes steps and asks before consequential actions.
- **Controlado:** Mosaic executes permitted low-risk steps and asks for approval at configured boundaries.
- **Autonomia limitada:** Mosaic can continue independently within explicit tool, workspace, time, iteration, and resource limits; gated actions still require approval.

These are product labels, not permission logic. The Core resolves and enforces the effective policy. The UI must explain that profile choice does not override security restrictions.

If profile persistence or backend policy support is not implemented yet, do not show non-functional controls. Initially expose only the profile actually enforced.

## 9. Final result and artifacts

On completion, show:
1. A concise summary of what was accomplished.
2. Files/artifacts with name, type, and safe open/download action.
3. Relevant checks performed and their outcomes.
4. Important limitations or failed steps.
5. A collapsible execution timeline.
6. Actions such as “Continuar nesta conversa”, “Tentar novamente” or “Abrir artefato” only when supported.

Do not mark a task complete solely because the model returned a final message. Completion must follow the Core’s task lifecycle and validation policy.

## 10. Errors, cancellation and reconnection

- Every active task exposes a visible **Cancelar tarefa** action.
- Cancellation is a request to the Core; UI must wait for the authoritative state.
- Show errors in plain language and provide a useful next action when possible.
- Keep diagnostic detail expandable; redact secrets and sensitive values.
- If SSE disconnects, show “Reconectando…” and recover the current task/event state from the backend.
- Do not start a duplicate task just because the browser reconnected.
- Distinguish provider failure, tool failure, permission denial, validation failure, user cancellation, and connection loss when the Core provides those distinctions.
- Do not silently discard partial results.

## 11. Observability without overwhelming the user

Default view:
- current activity;
- recent meaningful steps;
- approval cards;
- final result.

Details view:
- event timestamp;
- component/event type;
- tool name and safe arguments;
- whether it was proposed, approval-gated, approved, executed, or rejected;
- status/exit code where applicable, duration, and redacted bounded result/error;
- source URLs and artifact paths created/modified where applicable;
- relevant file/source references;
- task and tool-call identifiers for diagnostics.

Logs are not a place to display hidden chain-of-thought, secrets, raw environment variables, access tokens, or unbounded command output. Show concise rationale and observable evidence instead.

## 12. API and event contract

The frontend consumes existing and future Core APIs; it must not implement execution logic locally.

The Harness contract v1.2 is authoritative for backend semantics. Before wiring screens, inspect actual endpoints and schemas in the repository. Do not invent endpoints and assume they exist.

Expected frontend capabilities, to be mapped to actual API routes:
- list/create/select conversations and projects;
- list enabled models and select a model;
- send chat messages and consume streamed responses;
- create/read/cancel Tasks;
- read Task status and plan;
- list pending approval requests and submit decisions;
- read ToolCalls and ToolResults when exposed;
- subscribe to task/execution events through SSE;
- list/open/download artifacts;
- inspect source references and relevant logs where available.

### 12.1 Event handling

Treat events as updates to a persisted execution, not as the sole source of truth. Each event should have stable identity/order or another deduplication mechanism. The frontend should tolerate duplicate events, reconnects, and missed events by refreshing canonical task state.

Potential user-facing event categories:
- task lifecycle;
- plan update;
- step started/completed;
- approval required/decided;
- tool started/completed/failed;
- artifact created;
- validation completed;
- task completed/failed/cancelled.

Do not expose raw internal event names directly as user-facing copy.

## 13. Accessibility and responsive behavior

- Keyboard-accessible controls and visible focus states.
- Semantic buttons, labels and status announcements for screen readers.
- Never rely on colour alone.
- Respect reduced-motion preferences.
- Keep approval actions clear and separated to reduce accidental selection.
- On mobile, task timeline and details use a drawer or stacked view; no horizontal scrolling for core actions.
- Streaming content must not steal focus or repeatedly announce the entire transcript.

## 14. Visual direction

Aim for a calm, focused AI workspace:
- clear hierarchy;
- restrained colour;
- status colour only where meaningful;
- compact timeline;
- expandable technical detail;
- no animated “thinking brain” or fake terminal output;
- no fabricated token counters, progress percentages, or success indicators.

Use the existing design system and components when practical. Avoid introducing a UI library solely for decorative effects.

## 15. Implementation sequence

Implement in small, verifiable increments:

### Frontend Phase 0 — Audit
- Inspect existing React routes, components, API client, styles, and tests.
- Map each required UX capability to an existing endpoint/schema.
- Document missing backend contracts rather than mocking permanent behavior.
- Run the current frontend build/tests and record baseline.

### Frontend Phase 1 — Task status surface
- Display Task status in friendly language.
- Add an execution panel and timeline using real backend state.
- Handle loading, empty, error, cancellation, and reconnect states.

### Frontend Phase 2 — Approval loop
- Display pending approvals and action details.
- Submit decisions through Core APIs.
- Verify task resumption and duplicate-submission behavior end-to-end.

### Frontend Phase 3 — Results and artifacts
- Display final result, generated artifacts, and validation summary.
- Keep the task trace accessible after completion.

### Frontend Phase 4 — Execution settings
- Expose only implemented execution profiles and actual supported settings.
- Add Skills/settings views only when corresponding backend contracts exist.
- Add project instruction file discovery/selection UI only when Core APIs expose actual discovered files, scope, freshness and applied-source metadata; do not treat file contents as permissions.

### Frontend Phase 5 — Observability
- Add filters and technical details for events, ToolCalls, ToolResults and source references.
- Keep the friendly timeline as the default.

Do not implement all phases in one commit. Each phase requires focused tests and a reviewable diff.

## 16. Acceptance criteria

The frontend contract is satisfied when:

1. A normal chat does not accidentally start an agentic Task.
2. A user can start a Task and understand its goal and current status.
3. The timeline reflects real Core state and events.
4. An approval-required operation pauses visibly and can be approved or rejected.
5. The Core remains the only authority that decides whether an action executes.
6. A task can be cancelled and its final state is reflected correctly.
7. Reload/reconnect recovers task state without duplicating execution.
8. Completed tasks display their result and artifacts.
9. Failures are understandable and diagnostic detail is available without exposing secrets.
10. The interface works on narrow screens and via keyboard.
11. The existing chat/project/model experience is preserved.
12. Build and focused tests pass, and the commit contains no unrelated refactor.

## 17. Chat 01 workflow

For each frontend phase:
1. Read this contract and Harness contract v1.2.
2. Inspect the current repository and identify real routes/schemas.
3. State the exact gap before coding.
4. Implement only the next approved increment.
5. Add/update focused tests.
6. Run frontend build and relevant tests.
7. Review the diff and verify API compatibility.
8. Commit with a focused message.
9. Report files changed, tests/build results, known limitations, and commit SHA.
10. Stop before the next phase unless explicitly instructed.

If this contract conflicts with the current backend API, do not hide the mismatch with fabricated frontend state. Report it and propose the smallest coordinated Core/API change.

## 18. Final UX principle

**Mosaic should feel simple to use, while its work remains inspectable and controllable.**

The user sees the goal, meaningful progress, decisions that require them, and the result. The Core handles the complexity, security, state transitions, execution, and persistence.
