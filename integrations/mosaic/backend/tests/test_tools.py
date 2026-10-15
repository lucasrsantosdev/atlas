from pathlib import Path
from io import BytesIO

import pytest

from app.db.database import get_connection, init_db
from app.models.action_repository import create_action, update_action
from app.models.conversation_repository import create_conversation
from app.models.project_repository import create_project
from app.models.repository import create_model
from app.models.task_repository import create_task, update_task
from app.models.tool_call_repository import create_tool_call, get_tool_call, update_tool_call
from app.models.tool_result_repository import get_tool_result
from app.services.tools import approve_tool_call, execute_tool_call, resolve_tool_policy, validate_tool_call
from app.tools import registry
from app.tools.builtin import FilesystemTool, TerminalTool, WebFetchTool, _read_capped
from app.tools.safe_http import _SafeRedirectHandler, validate_public_url
from urllib.request import Request


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def _conversation(project_id=None):
    model = create_model("Test", "ollama", "test:model")
    return create_conversation("Tools", model.id, project_id=project_id)


def test_registry_contains_initial_tools() -> None:
    names = {tool.name for tool in registry.list()}
    assert {"filesystem", "terminal", "search", "web_fetch", "calculator", "weather"} <= names


def test_tool_call_is_intent_until_approved() -> None:
    conversation = _conversation()
    call = create_tool_call(conversation.id, "calculator", {"expression": "2 + 3"})

    validate_tool_call(call)
    with pytest.raises(ValueError):
        execute_tool_call(call)

    approved = approve_tool_call(call)
    assert approved.status == "approved"


def test_calculator_execution_persists_result() -> None:
    conversation = _conversation()
    call = create_tool_call(conversation.id, "calculator", {"expression": "2 + 3"})
    result = execute_tool_call(approve_tool_call(call))

    assert result.status == "completed"
    assert result.data == {"result": 5}
    assert get_tool_call(call.id).status == "completed"
    assert get_tool_result(result.id) == result


def test_failed_tool_result_invariant() -> None:
    conversation = _conversation()
    call = create_tool_call(conversation.id, "calculator", {"expression": "unknown"})
    result = execute_tool_call(approve_tool_call(call))

    assert result.status == "failed"
    assert result.data is None
    assert result.error


def test_tool_schema_rejects_unknown_fields_and_invalid_ranges() -> None:
    calculator = registry.get("calculator")
    with pytest.raises(ValueError, match="Unknown argument"):
        calculator.validate({"expression": "2 + 2", "run_shell": True})

    weather = registry.get("weather")
    with pytest.raises(ValueError, match="maximum"):
        weather.validate({"latitude": 100, "longitude": 0})

    with pytest.raises(ValueError, match="number"):
        weather.validate({"latitude": True, "longitude": 0})


def test_filesystem_rejects_traversal_and_symlink_escape(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    tool = FilesystemTool()

    with pytest.raises(ValueError, match="traversal"):
        tool.execute({"operation": "read", "path": "../secret.txt"}, workspace=workspace)

    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    link = workspace / "escape.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is not available in this environment")
    with pytest.raises(ValueError, match="inside the active workspace"):
        tool.execute({"operation": "read", "path": "escape.txt"}, workspace=workspace)


def test_filesystem_write_requires_explicit_overwrite(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    tool = FilesystemTool()
    created = tool.execute({"operation": "create", "path": "notes/one.txt", "content": "first"}, workspace=workspace)
    assert created["written"] is True
    assert (workspace / "notes" / "one.txt").read_text(encoding="utf-8") == "first"

    with pytest.raises(FileExistsError):
        tool.execute({"operation": "write", "path": "notes/one.txt", "content": "second"}, workspace=workspace)

    tool.execute({"operation": "write", "path": "notes/one.txt", "content": "second", "overwrite": True}, workspace=workspace)
    assert (workspace / "notes" / "one.txt").read_text(encoding="utf-8") == "second"


def test_filesystem_execution_uses_project_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "project-workspace"
    project = create_project("test", str(workspace))
    conversation = _conversation(project.id)
    task = create_task(type="generic", mode="agent", conversation_id=conversation.id, project_id=project.id)
    call = create_tool_call(
        conversation.id,
        "filesystem",
        {"operation": "create", "path": "result.txt", "content": "verified"},
        task_id=task.id,
    )
    result = execute_tool_call(approve_tool_call(call))
    assert result.status == "completed"
    assert (workspace / "result.txt").read_text(encoding="utf-8") == "verified"


def test_terminal_rejects_shell_operators_and_unapproved_commands(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    tool = TerminalTool()
    with pytest.raises(ValueError, match="Shell operators"):
        tool.execute({"command": "pwd; whoami"}, workspace=workspace)
    with pytest.raises(ValueError, match="allowlist"):
        tool.execute({"command": "whoami"}, workspace=workspace)


def test_terminal_runs_allowlisted_command_in_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    result = TerminalTool().execute({"command": "pwd"}, workspace=workspace)
    assert result["status"] == "success"
    assert Path(result["stdout"].strip()).resolve() == workspace.resolve()



def test_task_action_and_tool_call_transitions_are_enforced() -> None:
    conversation = _conversation()
    task = create_task(type="generic", mode="agent", conversation_id=conversation.id)
    with pytest.raises(ValueError, match="Invalid task transition"):
        update_task(task.id, status="completed")

    action = create_action(task.id, type="test")
    with pytest.raises(ValueError, match="Invalid action transition"):
        update_action(action.id, status="completed")

    call = create_tool_call(conversation.id, "calculator", {"expression": "1 + 1"}, task_id=task.id)
    with pytest.raises(ValueError, match="Invalid tool call transition"):
        update_tool_call(call.id, status="completed")



def test_public_web_fetch_blocks_local_and_non_http_destinations() -> None:
    with pytest.raises(ValueError, match="non-public"):
        validate_public_url("http://127.0.0.1/admin")
    with pytest.raises(ValueError, match="non-public"):
        validate_public_url("http://[::1]/")
    with pytest.raises(ValueError, match="HTTP and HTTPS"):
        validate_public_url("file:///etc/passwd")


def test_web_fetch_has_strict_schema() -> None:
    tool = WebFetchTool()
    with pytest.raises(ValueError, match="Unknown argument"):
        tool.validate({"url": "https://example.com", "allow_private": True})



def test_terminal_timeout_cleans_up_process_tree(tmp_path: Path, monkeypatch) -> None:
    from app.tools import builtin

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "test_wait.py").write_text(
        "import time\ndef test_wait():\n    time.sleep(5)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(builtin, "COMMAND_TIMEOUT_SECONDS", 0.3)
    result = TerminalTool().execute({"command": "python -m pytest test_wait.py"}, workspace=workspace)
    assert result["status"] == "timeout"
    assert result["duration_ms"] < 3_000


def test_terminal_cooperatively_cancels_running_task_command(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "test_wait.py").write_text(
        "import time\ndef test_wait():\n    time.sleep(5)\n",
        encoding="utf-8",
    )
    checks = 0

    def cancel_after_start() -> bool:
        nonlocal checks
        checks += 1
        return checks >= 4

    result = TerminalTool().execute(
        {"command": "python -m pytest test_wait.py"},
        workspace=workspace,
        cancel_check=cancel_after_start,
    )
    assert result["status"] == "cancelled"
    assert result["duration_ms"] < 3_000



def test_public_web_fetch_rejects_private_dns_and_redirects(monkeypatch) -> None:
    import socket

    monkeypatch.setattr(
        "app.tools.safe_http.socket.getaddrinfo",
        lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.8", 80))],
    )
    with pytest.raises(ValueError, match="non-public"):
        validate_public_url("http://public-looking.example/path")

    handler = _SafeRedirectHandler()
    with pytest.raises(ValueError, match="non-public"):
        handler.redirect_request(
            Request("https://example.com"),
            None,
            302,
            "Found",
            {},
            "http://169.254.169.254/latest/meta-data/",
        )


def test_search_results_are_normalized() -> None:
    from app.tools.builtin import _SearchResultsParser

    parser = _SearchResultsParser()
    parser.feed(
        '<div class="result"><a class="result__a" href="https://example.com/page">Example title</a>'
        '<div class="result__snippet">A short source snippet.</div></div>'
    )
    assert parser.results == [{
        "title": "Example title",
        "url": "https://example.com/page",
        "snippet": "A short source snippet.",
    }]



def test_calculator_rejects_excessive_exponents() -> None:
    calculator = registry.get("calculator")
    with pytest.raises(ValueError, match="exponent"):
        calculator.execute({"expression": "2 ** 1000000000"})



def test_new_work_items_cannot_start_in_terminal_or_approved_states() -> None:
    conversation = _conversation()
    with pytest.raises(ValueError, match="start in pending"):
        create_task(type="generic", mode="agent", conversation_id=conversation.id, status="completed")
    task = create_task(type="generic", mode="agent", conversation_id=conversation.id)
    with pytest.raises(ValueError, match="start in pending"):
        create_action(task.id, type="test", status="approved")
    with pytest.raises(ValueError, match="start in pending"):
        create_tool_call(conversation.id, "calculator", {"expression": "1 + 1"}, task_id=task.id, status="approved")



def test_core_policy_requires_approval_for_external_requests() -> None:
    calculator = resolve_tool_policy("calculator", {"expression": "1 + 1"})
    search = resolve_tool_policy("search", {"query": "Mosaic project"})
    fetch = resolve_tool_policy("web_fetch", {"url": "https://example.com"})

    assert calculator["approval_required"] is False
    assert search["approval_required"] is True
    assert fetch["approval_required"] is True



def test_terminal_output_capture_is_bounded() -> None:
    output = bytearray()
    truncated = {"stdout": False}
    _read_capped(BytesIO(b"x" * 100), output, 16, truncated, "stdout")
    assert len(output) == 16
    assert truncated["stdout"] is True
