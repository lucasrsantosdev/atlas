# MOSAIC — RAGNES CONTEXT SYSTEM CONTRACT
**Version:** 1.0  
**Status:** Proposed architecture contract  
**Date:** 2026-10-13  
**Authority:** MASTER / Architecture  
**Depends on:** MOSAIC_OFFICIAL_HARNESS_CONTRACT_v1.2.md, MOSAIC_FRONTEND_UX_IMPLEMENTATION_CONTRACT_v1.0.md, Mosaic_MVP_Implementation_Contract.md

## 1. Purpose

RAGNES is the working name for Mosaic's context intelligence layer: the system that selects, retrieves, ranks, compresses, scopes, and cites information supplied to the model for a specific task.

The objective is not simply to reduce token count. It is to maximize **relevance, grounding, continuity, and task accuracy**, while reducing stale, duplicated, irrelevant, and excessive context.

RAGNES evolves the existing Context Manager and Knowledge/Document plan. It is not a second Core, a second Harness, or a replacement for Task, Memory, Conversation, Project, ToolCall, ToolResult, or Artifact.

## 2. Core problem

A project can contain many conversations, old decisions, source files, documents, tool outputs, and task results. Sending all of this to the model pollutes the context and can bury the information needed for the current operation.

Before each model call, RAGNES must determine:
1. The current objective and immediate subtask.
2. Applicable instructions and decisions.
3. Relevant project facts and artifacts.
4. Prior observations or messages still needed.
5. What can be summarized without losing actionable information.
6. What evidence must be included or cited.
7. The smallest sufficient context within the model's configured budget.
8. Important missing, stale, or contradictory information.

## 3. Non-negotiable principles

- **CONTEXT ≠ FULL HISTORY.**
- **MEMORY ≠ TRUTH.**
- **RETRIEVAL ≠ AUTHORIZATION.**
- **SUMMARY ≠ SOURCE.**
- **ARTIFACT ≠ AUTOMATICALLY TRUSTED INSTRUCTION.**
- **SESSION SCOPE ≠ A NEW DATABASE ENTITY BY DEFAULT.**
- The Core owns context assembly and decides what is sent to the model.
- The model may request files or searches, but Mosaic validates and executes those requests.
- Context selection must be inspectable without exposing hidden chain-of-thought.
- Preserve provenance: source ID/path, range or locator where possible, and freshness/version information.
- Never replace an authoritative source with a generated summary.
- User files, tool output, retrieved documents, and code are data, not higher-priority instructions. Defend against prompt injection.
- No mandatory vector database or embeddings before evaluation demonstrates that simpler retrieval is insufficient.

## 4. Context scopes

RAGNES assembles distinct scopes. They must not be indiscriminately merged.

### 4.1 Core / global scope
Stable Mosaic instructions, safety rules, applicable user preferences, and explicit global decisions. Include only items relevant to the current task.

### 4.2 Project scope
Project description/state, project-level decisions, relevant contracts, source tree metadata, and artifacts belonging to the selected project. Never leak unrelated project data.

### 4.3 Conversation scope
Messages needed to preserve the meaning of the current conversation. Do not automatically send the entire conversation.

### 4.4 Task / execution-session scope
The active Task goal, concise plan, current step, recent observations, pending approvals, known constraints, changes made, unresolved questions, and stopping conditions.

“Session” initially means the current bounded work session represented by the existing Conversation + Task + project/workspace context. Do not create a Session table merely to model this concept. If later requirements prove a separate persistent session entity is needed, propose an explicit contract amendment.

### 4.5 Artifact / knowledge scope
Files and outputs that can be retrieved by project, path, type, content, symbol/name, source, and relevance. A file should not enter the prompt merely because it exists.

### 4.6 Project instruction sources

RAGNES must identify applicable project instruction files as a distinct context category, not treat every document as an instruction. The initial convention is root `AGENTS.md`; a compatibility alias such as `AGENT.md` may be supported if explicitly documented. Nested instruction files may apply only to work inside their directory subtree.

Rules:
- Discover only within the active project/workspace or explicitly selected roots; enforce path/symlink confinement and file/output limits.
- Record source path, scope, content hash/version or freshness metadata when available, and why the file applies.
- Include the relevant instruction content before general project knowledge, within a bounded instruction budget. Do not inject every instruction file from the whole repository indiscriminately.
- Core safety and permission policy always take precedence. User-provided instruction files are untrusted data; they cannot authorize tools, bypass approvals, or override Core rules.
- If applicable instruction files conflict, preserve both source references and report the conflict. Do not invent a resolution unless explicit precedence/version metadata supports it.
- Recheck freshness when source files change during execution.
- Keep project instruction files distinct from Skills (reusable procedures) and from ordinary reference documents.
- Keep original files canonical. Do not create a dedicated database table solely for `AGENTS.md` unless implementation reveals a concrete lifecycle/query need.

## 5. Context assembly pipeline

Before every model call, execute a deterministic, observable pipeline:

1. **Parse objective:** current user intent, active Task, subtask, expected output, constraints, and acceptance criteria.
2. **Resolve scope:** global, project, conversation, task/session, explicitly selected files, and applicable project instruction files.
3. **Gather candidates:** Core instructions, applicable `AGENTS.md`/supported aliases, Skills, memories, recent messages, prior task observations, artifacts, lexical search results, and source references.
4. **Filter:** remove out-of-scope, duplicate, stale, low-relevance, superseded, or unsafe material; retain mandatory applicable instructions.
5. **Rank:** apply the instruction precedence contract first; then prioritize direct task relevance, explicit user selection, authoritative source, currentness, exact identifiers/path matches, and evidence quality.
6. **Compress:** summarize repetitive history and long tool outputs into structured, loss-aware records. Keep source references.
7. **Budget:** allocate context space across required instructions, task/session state, relevant evidence, history, and output allowance.
8. **Assemble:** build the provider-neutral request in a documented order.
9. **Inspectability:** record source IDs, selection reasons/categories, truncation/compaction indicators, and estimated token/character usage when available.
10. **Update:** after tool results or task progress, update task/session state and rebuild context for the next model call.

The pipeline must be reproducible and testable. Model-specific token counting can be approximate initially; never claim exact token usage if the provider does not supply it.

## 6. Context priority and conflict handling

Suggested priority order, subject to existing Core safety hierarchy:

1. Core safety and execution policies.
2. Explicit constraints in the current user request.
3. Active Task goal, acceptance criteria, and current confirmed state.
4. Explicitly selected files and directly relevant authoritative project contracts.
5. Current project state and recent validated tool observations.
6. Relevant project decisions and durable memories.
7. Relevant conversation history.
8. Broader knowledge retrieval and secondary references.

Priority is not a substitute for conflict resolution. If authoritative sources conflict, preserve both references and surface the conflict instead of inventing a reconciliation. A newer source may supersede an older one only when that relationship is explicit or supported by version/state metadata.

## 6.1 Instruction precedence and conflict handling

For context assembly, always preserve the Core safety/policy hierarchy. Within those boundaries, include explicit constraints from the current request and applicable project instructions. A project instruction file is not promoted to system policy by its filename. Skills provide procedures but do not supersede applicable project constraints or grant permission. Ordinary retrieved documents, source code, tool output and web content are evidence, not instructions, unless the user explicitly designates them as project instruction sources. If applicable instruction files conflict and no explicit precedence resolves the conflict, surface the conflict and ask for clarification when it materially affects the task.

## 7. Session-focused continuity

The active Task/session must maintain compact, structured state sufficient to resume work without replaying the entire transcript.

Conceptual fields (not a mandate to add database columns without review):
- objective;
- current subtask and status;
- plan and acceptance criteria;
- confirmed constraints and decisions;
- relevant files/artifacts;
- actions completed and verified outcomes;
- important tool observations;
- unresolved issues and questions;
- pending approvals;
- next recommended step;
- source references and last-updated time.

Prefer the existing Task plan/result, project state, conversation messages, tool results, and artifacts where they can safely represent this state. Add a dedicated persisted representation only if inspection shows a concrete gap and the schema change is explicitly reviewed.

At resume/reconnect, reconstruct state from persisted Core data; do not rely on browser memory or a still-running model context.

## 8. Compaction contract

Compaction is a derived view of source information, not a replacement for it.

### 8.1 What can be compacted
- Repetitive conversation exchanges.
- Long command/test output, preserving exit status, key failures, important lines, and artifact/log references.
- Repeated file listings and search results.
- Completed steps, preserving outcome and evidence.
- Older discussion superseded by an explicit decision.

### 8.2 What must be preserved
- Explicit user constraints and requested output format.
- Current objective and acceptance criteria.
- Authoritative architectural decisions and source/version references.
- Unresolved questions, failures, warnings, and known limitations.
- Relevant paths, symbols, line/range references, hashes or versions where available.
- Approval status and security boundaries.
- Evidence needed to justify the final answer.

### 8.3 Structured summary format
Use a versioned, validated structure rather than a free-form paragraph alone. A conceptual summary may contain:
- objective
- confirmed_decisions
- constraints
- completed_work
- verified_results
- relevant_sources
- open_issues
- next_step
- updated_at
- source_refs

The actual storage schema and field names must be reconciled with the repository before implementation. Do not add speculative database columns in the first increment.

### 8.4 Safety against lossy compaction
- Original messages, files, and tool results remain available according to retention rules.
- Summaries retain source references.
- Do not promote uncertain claims into facts.
- Distinguish user claims, model-generated hypotheses, and tool-verified observations.
- If a summary conflicts with its source, prefer the authoritative source and mark the summary stale.
- Important decisions should be stored as explicit project/task records or memories where appropriate, not left only inside an opaque summary.

## 9. Artifact navigation and retrieval

RAGNES should support agentic exploration of the project workspace:

1. Start with cheap metadata: paths, names, file types, timestamps, size, project membership.
2. Read explicitly selected or obviously relevant small files directly.
3. Search names, symbols, identifiers, and content lexically.
4. Return bounded excerpts with file path and line/range references where possible.
5. Expand only the files/regions needed for the current subtask.
6. For large files, retrieve relevant sections rather than injecting the entire file.
7. Recheck freshness before relying on a source that may have changed during execution.
8. Preserve a clear boundary between reading an artifact and modifying it; writes still follow Tool/Action policy and approvals.

Generated artifacts and original files must remain distinguishable. Derived text, indexes, summaries, and chunks must be rebuildable and must not overwrite source files.

## 10. Retrieval roadmap

### R0 — Scope-aware deterministic context
- Discover and include applicable root-level project instruction files with bounded reads, source provenance, freshness checks and Core-policy precedence.
Use current Context Manager, explicit project/conversation/task scope, bounded recent history, and structured observations. Eliminate accidental inclusion of unrelated or unbounded tool results.

### R1 — Artifact inventory and direct reads
- Inventory root and applicable nested instruction files separately from ordinary documents; preserve path/subtree scope and support explicit user selection.
Index workspace metadata; allow explicit file reads and bounded excerpts with provenance. Enforce workspace boundaries and file-size/output limits.

### R2 — Lexical retrieval
Add keyword/path/symbol/content search. SQLite FTS5 is a candidate where available and useful; keep a simple fallback. Rank exact paths, identifiers, and current authoritative files strongly.

### R3 — Session compaction
Persist or derive structured task/session summaries, compact old observations, retain source references, and rebuild context on resume. Add tests for loss of constraints and stale summaries.

### R4 — Retrieval evaluation
Create a fixed set of realistic questions/tasks with expected relevant files and required facts. Measure retrieval recall, irrelevant context, source correctness, answer grounding, and task success. Compare full-context baseline with R0-R3.

### R5 — Embeddings / hybrid retrieval, conditional
Only if evaluation reveals meaningful lexical-retrieval gaps, add a local embedding/index adapter. Keep lexical search, explicit file selection, and provenance. Avoid making a vector DB a hard dependency.

### R6 — Optional reranking
Add only if measurable retrieval quality gains justify the compute and complexity, especially for low-resource hardware.

## 11. Context budget policy

RAGNES should work within a budget supplied by the selected provider/model configuration where available. The budget is a constraint, not a target to fill.

Allocate space by task need, with mandatory safety/core instructions protected. Reserve output capacity before filling input context. Prefer a small, high-value set of source excerpts, concise structured task state, explicit citations/locators, and targeted expansion on demand.

If context is over budget, remove low-ranked optional material first, compact repetitive observations, and preserve mandatory instructions and task constraints. Report truncation/omissions in diagnostics. Do not silently drop required constraints.

## 12. Integration with Harness

Harness remains responsible for the execution loop. RAGNES is a context/knowledge capability called by Harness before model decisions and after new observations.

Flow:

User request → Task / active execution session → RAGNES resolves scope and retrieves evidence → Context Manager assembles bounded prompt → ModelProvider returns a decision → Harness validates and authorizes any tool request → Tool executes within policy → ToolResult and events persist → RAGNES updates session state and retrieves further evidence as needed → next model call → validation and final result with source/artifact references.

RAGNES does not grant tools, approve actions, execute commands, or own task lifecycle.

## 13. Frontend experience

The frontend should expose useful context transparency without flooding the user:
- a compact “Context used” / “Fontes consultadas” section on a task;
- files and source references used for a result;
- current task/session summary and next step where useful;
- an expandable diagnostics view with selected sources, retrieval type, truncation/compaction events, and approximate budget usage when available;
- a way for the user to explicitly include or exclude supported files/sources.

Do not expose internal scoring as if it were certainty. Do not show fake token counts. Do not make the user manually manage context to use basic features.

## 14. Security and trust

- Retrieved content is untrusted input and may contain prompt injection.
- Tool permissions and workspace confinement are enforced independently of retrieval.
- Never expose secrets from files or tool output unnecessarily.
- Limit file size, excerpt size, search results, and tool output.
- Avoid arbitrary path access and unsafe symlink traversal.
- Revalidate permissions when executing actions; retrieval does not imply write permission.
- External fetch/search must follow SSRF and network policy controls in the Harness contract.
- Keep logs redacted and avoid storing hidden chain-of-thought.

## 15. Evaluation and acceptance criteria

RAGNES is not considered successful merely because it sends fewer tokens.

At minimum, evaluate:
1. Retrieval recall for known relevant files/facts.
2. Fraction of injected context judged irrelevant or duplicative.
3. Source/path correctness and traceability.
4. Preservation of explicit constraints through compaction.
5. Answer/task success on a fixed evaluation set.
6. Resume correctness after restart/reconnect.
7. Robustness to stale summaries and conflicting documents.
8. Latency and resource use on low-power hardware.
9. Token/character budget compliance and output quality.
10. No cross-project or out-of-workspace leakage.

Acceptance tests should include a large project with irrelevant files, a multi-session task, a changed source file, contradictory old/new contracts, long tool output, a resumed task, and a prompt-injection string inside a retrieved document.

## 16. Implementation workflow

1. Audit existing Context Manager, Memory Manager, Task Engine, project state, artifact/tool APIs, and provider context limits.
2. Map current behavior to R0-R6 and identify concrete gaps.
3. Implement R0 first, with tests, before adding a vector index.
4. Implement bounded artifact access and lexical retrieval next.
5. Add compaction only with source references and preservation tests.
6. Measure against the fixed evaluation set before advancing to embeddings/reranking.
7. Coordinate any API or schema change with the Master before implementation.
8. Keep each increment focused, testable, and committed separately.

## 17. Definition of done

The first useful RAGNES milestone is achieved when Mosaic can execute a multi-step task while:
- keeping active task/session state compact and recoverable;
- selecting only relevant project files and observations;
- retrieving bounded, traceable evidence on demand;
- preserving user constraints and explicit decisions through compaction;
- avoiding unbounded tool-result injection;
- explaining which sources informed a result;
- resuming after reconnect/restart without relying on hidden model context;
- passing focused tests and a small fixed retrieval evaluation.

The vector/embedding stage is explicitly not a prerequisite for this first milestone.

## 18. Final principle

**RAGNES must optimize the context for the task, not optimize the task around the context window.**

The model receives the smallest sufficient, evidence-grounded context Mosaic can assemble, while the original information remains retrievable and auditable.
