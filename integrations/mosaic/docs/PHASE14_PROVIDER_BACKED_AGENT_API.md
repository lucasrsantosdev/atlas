# Phase 14 — Provider-backed agent decision API

## Goal
Connect the existing agent loop to the configured real ModelProvider and expose an explicit API action to start an agent-mode Task. Chat remains the default path and is not converted into a Task automatically.

## Implementation
- Adds a provider-neutral JSON decision envelope: `final` or `tool_call`.
- Uses the configured conversation model through the existing Ollama ModelProvider.
- Includes registered tool names, descriptions and input schemas in the decision prompt.
- Validates the model's JSON envelope and tool arguments before returning a decision to the agent loop.
- Adds `POST /tasks/start` to persist the user's goal as a conversation message, create an agent Task, and schedule execution. Also adds `POST /tasks/{task_id}/run` for an existing pending agent Task. Both claim the Task before scheduling the loop.
- Uses existing Task, ToolCall, ToolResult and TaskEvent persistence. No schema or dependency changes.

## Boundaries / limitations
- This increment does not implement approval decision/resume; approval-required operations still pause in `awaiting_approval`. The next increment must implement same-Task/same-ToolCall resume before the full approval loop is complete.
- FastAPI BackgroundTasks is an in-process execution mechanism, not a durable job queue. A process restart can interrupt an active run; persisted state/events remain available, but restart recovery is not claimed here.
- Only the existing Ollama provider is supported by this adapter.
- No live Ollama call, test suite or frontend build has been run by the implementation agent. Treat this as implemented in source, not runtime-verified.

## Validation
Run from `backend`:
```bash
python -m pytest tests/test_agent_decision.py tests/test_agent_task_api.py tests/test_agent.py tests/test_task_events.py -q
python -m pytest -q
```
