# Phase 7 — Task events and reconnectable timeline API

## Schema decision

Add the purpose-specific `task_events` table required by Harness v1.2. It is not a generic audit log. It stores bounded operational events needed to reconstruct a task timeline and query events after a cursor.

- Identity/order: autoincrement `id`; timestamp is UTC ISO-8601.
- Scope: required `task_id`; optional conversation/project/tool_call/action identifiers with foreign keys.
- Payload: level, component, event name, concise message, optional duration/status, bounded redacted JSON metadata.
- Deletion: events cascade with task deletion; optional relationship references are nulled when their source record is deleted.
- Migration: additive `CREATE TABLE IF NOT EXISTS` and indexes during normal initialization; no existing table or user data is rewritten.
- Retention: MVP keeps task-linked events with the task; bounded per-event message/metadata, with list API capped at 200 events per request. Whole-store retention/compaction remains a later operational decision.

## Scope in this increment

- Persist task creation/status changes and tool proposal/status changes.
- Expose ordered task event retrieval using `after_id` cursor for refresh/reconnect.
- Add an SSE stream that honors `Last-Event-ID`, emits ordered event IDs and keep-alives, and closes after a bounded 30-second window so clients can reconnect.
- Redact metadata keys likely to contain secrets and bound metadata/message sizes.
- No broker, external logging service, new service process, or schema unrelated to the event timeline.

## Validation

From `backend/`:

```bash
python -m pytest tests/test_task_events.py tests/test_task.py tests/test_agent.py tests/test_harness.py tests/test_tools.py tests/test_action.py -q
```

Runtime test execution has not been performed by the implementation assistant.
