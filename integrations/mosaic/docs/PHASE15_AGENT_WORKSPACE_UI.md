# Phase 15 — Agent Task workspace UI

## Goal
Make the existing “Tarefas” project tab a functional view of persisted Core Tasks while preserving the normal chat experience.

## Implemented in source
- Adds a frontend API client for listing/getting Tasks, starting a Task from a goal, reading persisted events and requesting cancellation.
- Adds a Task workspace with a goal composer that calls `POST /tasks/start`.
- Lists Tasks belonging to the active conversation, displays the actual persisted status and lets the user select an execution.
- Refreshes the selected Task and its persisted event timeline every 2.5 seconds; reopening/selecting a Task reloads state from the API rather than trusting only transient UI state.
- Displays the final output or persisted error when present, plus a cancel control for active states.
- Keeps the normal chat composer and message stream available in the Conversa tab.
- Adds responsive styles for task list, status indicators, timeline, result and mobile layout.

## Contract boundaries
- The Core remains authoritative for Task state. The UI does not invent progress percentages; the moving line is a generic activity indicator only while a Task is active.
- Approval UI and same-Task resume are not implemented here. When a Task reaches `awaiting_approval`, the UI explicitly explains that approval interaction is the next increment.
- ToolCall/ToolResult detail, artifact list and reconnecting SSE subscription are not yet implemented. Timeline recovery currently uses bounded REST refresh of persisted events.
- The other project tabs (Files, Memory, Artifacts, Notes) are not made functional by this increment.

## Validation
The implementation agent did not execute the frontend production build or browser tests. Run:
```bash
cd frontend
npm run build
```
Then run the backend tests from the Phase 14 PR and verify against a running Core/Ollama instance:
1. Start an agent task from the Tarefas tab.
2. Confirm its persisted state and timeline update.
3. Reload the page and reselect the task; verify state/result is recovered.
4. Cancel an active task and confirm the persisted status changes.
5. Confirm normal chat still works from the Conversa tab.
