# Mosaic — Phase 1 Tool Hardening

**Branch:** `codex/phase1-tool-hardening`  
**Scope:** first implementation increment for filesystem, terminal, tool validation, persisted state transitions and public web access.

## Run the focused backend checks

From the repository root:

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest tests/test_tools.py tests/test_task.py tests/test_action.py tests/test_agent.py -q
```

The current ChatGPT implementation environment could not resolve `github.com`, so these tests have been added but were **not executed in this implementation session**. Run them in the local development environment before merging.

## Filesystem behavior

Filesystem operations are scoped to the workspace resolved by the Core from the persisted Task/Project/Conversation. A model-supplied path cannot choose the workspace root.

Supported operations: `list`, `read`, `create`, `write`, `mkdir`.

- Traversal segments (`..`) and paths resolving outside the active workspace are rejected.
- Symlinks that resolve outside the workspace are rejected; existing symlink path components are rejected where encountered.
- Reads and writes are capped at 1 MB; directory listings return at most 500 entries.
- `create` never overwrites an existing file.
- `write` refuses to replace an existing file unless `overwrite: true` is supplied.
- Writes use a temporary file and atomic replacement where supported.
- Binary content is not silently decoded as text.

## Terminal behavior

The terminal is deliberately an allowlisted non-interactive runner, not a general shell. It uses an argument list with `shell=False`, the active workspace as `cwd`, a reduced environment, a 30-second wall-clock limit, a 200 KB cap for each output stream, process-group cleanup on timeout, and cooperative cancellation when the associated Task becomes `cancelled`.

Initially supported commands include `pwd`, limited `ls`/workspace-scoped `cat`, `git status`, `git diff`, `git log`, `git ls-files`, `pytest`, `python -m pytest`, `python -m compileall .`, `npm run build` and `npm test`.

Terminal operations require approval. This is **not an OS-level sandbox**: test/build tools can execute project code, and no claim is made that subprocesses are unable to access resources available to the Mosaic process. The allowlist and approval reduce exposure but do not replace OS isolation.

## Public web operations

- `search` returns bounded, normalized result records with title, URL, snippet, rank, provider and retrieval timestamp.
- `web_fetch` is a separate capability for bounded text extraction from public HTTP(S) pages.
- Requests disable environment-configured proxies, validate public DNS/IP destinations, revalidate redirect destinations, restrict content types and cap response sizes.
- Outbound search, page fetch and weather requests require approval under the current default policy; the local calculator does not.

**Known network limitation:** urllib resolves a hostname again when connecting after the preflight DNS check. The guard blocks ordinary private/loopback/link-local/reserved destinations and unsafe redirects, but without a transport that pins the validated IP while preserving TLS hostname verification it cannot completely eliminate DNS-rebinding races. Do not describe it as perfect SSRF isolation.

## State consistency

Task, Action and ToolCall status updates validate the domain transition graph in the repository layer. Status updates use compare-and-set SQL predicates so a stale concurrent update cannot silently overwrite a newer state. Tool policy/schema validation runs in the Core before a model-proposed tool call is approved or executed.

## Still pending after this increment

- Full runtime execution of the focused tests and broader regression suite.
- A real-provider Harness integration and durable approval/resume flow.
- Persisted execution events and UI timeline.
- End-to-end cancellation/restart tests.
- Artifact/Setting schema reconciliation and artifact APIs.
- More complete cancellation and policy tests on Windows as well as POSIX.
