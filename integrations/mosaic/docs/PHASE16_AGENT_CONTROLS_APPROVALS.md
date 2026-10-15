# Phase 16 — Agent controls, approvals, and inspection

## Implemented
- Adds a persisted decision endpoint for the pending ToolCall associated with a Task in `awaiting_approval`.
- Approval revalidates the registered tool policy, executes the approved call, transitions the same Task back to `executing`, and schedules the provider-backed loop to continue. Rejection records the ToolCall as rejected and ends the Task with an explicit user-rejection result.
- Adds read-only ToolCall/ToolResult inspection endpoints for a conversation and optional Task.
- Adds project agent configuration API: root `AGENTS.md` plus up to 12 named skills stored in project state.
- Applies `AGENTS.md` and enabled skill text to future context assembly within explicit size bounds. These are user-authored, untrusted project guidance; they do not grant tools or bypass Core policy.
- Adds frontend approval cards, operation-argument details, approve/reject controls, EventSource task timeline with browser-managed reconnect, and an “Agente” project tab to edit/save `AGENTS.md` and skills.
- Adds regression tests for instruction/skill persistence, symlink rejection, approval decision and same-Task resume scheduling.

## Limits and safety
- The editor writes only the root `AGENTS.md` within the project's configured workspace. It rejects an existing symlink at that path and bounds file size.
- Skills are persisted in the existing project `state` JSON; no new database table or dependency is introduced.
- Skills are guidance, not tool authorization. Core permission policies and approval gates remain authoritative.
- Approval/rejection are tied to the exact Task and its pending ToolCall; terminal or mismatched calls are rejected.
- The frontend uses the persisted Task/Event/ToolCall API as source of truth. It does not expose chain-of-thought.

## Validation not performed by the implementation agent
Run from `backend`:
```bash
python -m pytest tests/test_agent_controls.py tests/test_agent.py tests/test_agent_task_api.py tests/test_task_events.py -q
python -m pytest -q
```
Run from `frontend`:
```bash
npm run build
```
Then smoke-test a task that requests an approval-required filesystem or terminal operation, approve it, confirm the same Task resumes, and separately test rejection. Save `AGENTS.md` and an enabled skill, start a new Task, and confirm the model's context follows those instructions without bypassing tool approvals.
