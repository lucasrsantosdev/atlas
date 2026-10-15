# Phase 17 — Project files, artifacts, and remaining workspace tabs

## Implemented
- Brings the bounded RAGNES artifact inventory and UTF-8 excerpt reader into the provider-backed agent branch.
- Brings deterministic lexical workspace search and structured session compaction into the same context manager that loads `AGENTS.md` and enabled project skills.
- Exposes project-scoped APIs for inventory, direct excerpts with line provenance, and lexical search. Path traversal, symlink paths, non-text files, oversized reads, and out-of-workspace access are rejected by the underlying bounded reader.
- Frontend “Arquivos” and “Artefatos” tabs now show the workspace inventory, provide lexical search, and display bounded excerpts with source path and line range. The UI explicitly avoids claiming that a separate task-artifact registry exists.
- Adds ToolCall/ToolResult inspection to the Task view.
- Makes the “Memória” project tab support create, edit, and delete through the existing Core API.
- Makes the “Notas” tab persist notes in existing project metadata.
- Adds API regression tests for workspace inventory, excerpt and lexical search.

## RAGNES context behavior
- Explicitly named project-relative files can be retrieved as bounded evidence.
- If explicit paths yield no excerpt, the context manager may use deterministic lexical retrieval.
- Older conversation messages are compacted into a bounded source-linked summary while recent messages and canonical Task state remain available.
- Project instructions and enabled skills remain untrusted guidance and cannot authorize tools or bypass approval gates.

## Honest boundary
- The current Core has workspace files and tool results, but no independent persistent Artifact entity. “Artefatos” therefore surfaces files in the active project workspace; it does not label every file as produced by a particular Task.
- Notes are stored in existing project metadata; they are not automatically promoted to memory or agent instructions.
- The implementation agent did not execute backend tests or the frontend build.

## Validation
From `backend`:
```bash
python -m pytest tests/test_project_artifact_api.py tests/test_ragnes_r1_artifacts.py tests/test_ragnes_r1_context.py tests/test_ragnes_r2_search.py tests/test_ragnes_r2_context.py tests/test_ragnes_r3_compaction.py tests/test_agent_controls.py -q
python -m pytest -q
```
From `frontend`:
```bash
npm run build
```
Then smoke-test search and excerpt reading against a project workspace, reload the browser, edit instructions/skills, and confirm the next agent run receives the configured context.
