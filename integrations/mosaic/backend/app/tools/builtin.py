import ast
from datetime import datetime, timezone
import json
from itertools import islice
import math
import operator
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import threading
import time
from typing import Any, Callable
from urllib.parse import quote
from urllib.request import Request

from app.tools.safe_http import safe_urlopen

from app.tools.base import Tool

MAX_FILE_BYTES = 1_000_000
MAX_LIST_ENTRIES = 500
MAX_COMMAND_LENGTH = 2_000
MAX_PROCESS_OUTPUT_BYTES = 200_000
COMMAND_TIMEOUT_SECONDS = 30


def _require_workspace(workspace: Path | None) -> Path:
    if workspace is None:
        raise ValueError("An active project workspace is required for this tool")
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace.resolve(strict=True)


def _workspace_path(root: Path, raw_path: str, *, allow_root: bool = True) -> Path:
    if not raw_path or "\x00" in raw_path:
        raise ValueError("A non-empty valid workspace path is required")
    candidate_input = Path(raw_path)
    if any(part == ".." for part in candidate_input.parts):
        raise ValueError("Path traversal is not allowed")
    candidate = candidate_input if candidate_input.is_absolute() else root / candidate_input
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ValueError("Path must remain inside the active workspace") from exc
    if not allow_root and resolved == root:
        raise ValueError("The workspace root cannot be used for this operation")
    # Reject existing symlinks in every path component, even when they point inward.
    relative = resolved.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlink paths are not allowed in workspace operations")
    return resolved


class FilesystemTool(Tool):
    name = "filesystem"
    description = "List, read, create and write files inside the active project workspace."
    input_schema = {
        "type": "object",
        "required": ["operation", "path"],
        "additionalProperties": False,
        "properties": {
            "operation": {"type": "string", "enum": ["read", "write", "create", "mkdir", "list"], "maxLength": 16},
            "path": {"type": "string", "minLength": 1, "maxLength": 2048},
            "content": {"type": "string", "maxLength": MAX_FILE_BYTES},
            "overwrite": {"type": "boolean"},
        },
    }
    permission_policy = {"approval_required": True, "scope": "active_workspace"}

    def execute(self, arguments: dict[str, Any], *, workspace: Path | None = None, cancel_check: Callable[[], bool] | None = None) -> Any:
        root = _require_workspace(workspace)
        operation = arguments["operation"]
        path = _workspace_path(root, arguments["path"], allow_root=operation in {"list", "mkdir"})
        if operation == "read":
            path = _workspace_path(root, arguments["path"], allow_root=False)
            if not path.is_file():
                raise ValueError("The requested workspace file does not exist")
            with path.open("rb") as handle:
                raw = handle.read(MAX_FILE_BYTES + 1)
            if len(raw) > MAX_FILE_BYTES:
                raise ValueError("File exceeds the read limit")
            return {"operation": "read", "status": "success", "path": path.relative_to(root).as_posix(), "content": raw.decode("utf-8"), "bytes": len(raw)}
        if operation == "list":
            path = _workspace_path(root, arguments["path"], allow_root=True)
            if not path.is_dir():
                raise ValueError("The requested workspace directory does not exist")
            sampled = list(islice(path.iterdir(), MAX_LIST_ENTRIES + 1))
            truncated = len(sampled) > MAX_LIST_ENTRIES
            entries = sorted(item.name for item in sampled[:MAX_LIST_ENTRIES])
            return {"operation": "list", "status": "success", "path": "." if path == root else path.relative_to(root).as_posix(), "entries": entries, "count": len(entries), "truncated": truncated}
        if operation == "mkdir":
            path = _workspace_path(root, arguments["path"], allow_root=True)
            existed = path.is_dir()
            path.mkdir(parents=True, exist_ok=True)
            if not path.is_dir():
                raise OSError("Directory creation could not be verified")
            return {"operation": "mkdir", "status": "success", "path": "." if path == root else path.relative_to(root).as_posix(), "created": not existed}
        if operation in {"write", "create"}:
            content = arguments.get("content")
            if content is None:
                raise ValueError("content is required for write/create")
            if len(content.encode("utf-8")) > MAX_FILE_BYTES:
                raise ValueError("File content exceeds the write limit")
            overwrite = arguments.get("overwrite", False)
            existed = path.exists()
            if existed and not path.is_file():
                raise ValueError("The destination exists and is not a regular file")
            if existed and (operation == "create" or not overwrite):
                raise FileExistsError("File already exists; set overwrite=true to replace it")
            path.parent.mkdir(parents=True, exist_ok=True)
            # Re-check after parent creation immediately before the side effect.
            path = _workspace_path(root, arguments["path"], allow_root=False)
            existed = path.exists()
            if existed and not path.is_file():
                raise ValueError("The destination exists and is not a regular file")
            if existed and (operation == "create" or not overwrite):
                raise FileExistsError("File already exists; set overwrite=true to replace it")
            encoded = content.encode("utf-8")
            temporary = path.with_name(f".{path.name}.mosaic-tmp")
            try:
                with temporary.open("x", encoding="utf-8") as handle:
                    handle.write(content)
                if path.exists() and (operation == "create" or not overwrite):
                    raise FileExistsError("File already exists; set overwrite=true to replace it")
                os.replace(temporary, path)
                if not path.is_file() or path.stat().st_size != len(encoded):
                    raise OSError("Written file could not be verified")
            finally:
                if temporary.exists():
                    temporary.unlink()
            return {"operation": operation, "status": "success", "path": path.relative_to(root).as_posix(), "written": True, "created": not existed, "overwritten": existed, "bytes": len(encoded)}
        raise ValueError(f"Unsupported filesystem operation: {operation}")


def _validate_command(tokens: list[str], root: Path) -> None:
    if not tokens:
        raise ValueError("Command is empty")
    # Deliberately support common inspection and validation commands, not arbitrary shell.
    exact_commands = {
        ("pwd",), ("ls",), ("ls", "-la"), ("ls", "-al"),
        ("git", "status"), ("git", "diff"), ("git", "log"), ("git", "ls-files"),
        ("git", "diff", "--stat"), ("git", "log", "-5"),
        ("pytest",), ("python", "-m", "pytest"),
        ("python", "-m", "compileall", "."),
        ("npm", "run", "build"), ("npm", "test"),
    }
    if tuple(tokens) in exact_commands:
        return
    if tokens[:3] == ["python", "-m", "pytest"] and len(tokens) > 3:
        path_tokens = tokens[3:]
        if any(token.startswith("-") for token in path_tokens):
            raise ValueError("Command options are not supported for path-scoped commands")
        for raw in path_tokens:
            _workspace_path(root, raw)
        return
    if tokens[0] in {"cat", "ls", "pytest"} and len(tokens) >= 2:
        if any(token.startswith("-") for token in tokens[1:]):
            raise ValueError("Command options are not supported for path-scoped commands")
        for raw in tokens[1:]:
            _workspace_path(root, raw, allow_root=tokens[0] == "ls")
        return
    raise ValueError("Command is not in the supported non-interactive command allowlist")


def _read_capped(stream, output: bytearray, cap: int, truncation: dict[str, bool], key: str) -> None:
    while True:
        chunk = stream.read(8192)
        if not chunk:
            return
        remaining = cap - len(output)
        if remaining > 0:
            output.extend(chunk[:remaining])
        if len(chunk) > max(remaining, 0):
            truncation[key] = True


def _stop_process_tree(process: subprocess.Popen) -> None:
    try:
        if os.name == "nt":
            if process.poll() is not None:
                return
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=5, check=False,
            )
        else:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                return
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
            # Kill the process group even if its leader exited but a child retained the pipes.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    except (OSError, subprocess.SubprocessError):
        if process.poll() is None:
            process.kill()


class TerminalTool(Tool):
    name = "terminal"
    description = "Run a limited set of non-interactive inspection and validation commands in the active workspace."
    input_schema = {
        "type": "object",
        "required": ["command"],
        "additionalProperties": False,
        "properties": {"command": {"type": "string", "minLength": 1, "maxLength": MAX_COMMAND_LENGTH}},
    }
    permission_policy = {"approval_required": True, "scope": "active_workspace", "timeout_seconds": COMMAND_TIMEOUT_SECONDS}

    def execute(self, arguments: dict[str, Any], *, workspace: Path | None = None, cancel_check: Callable[[], bool] | None = None) -> Any:
        root = _require_workspace(workspace)
        command = arguments["command"]
        if re.search(r"[|;&><\x60$()\n\r]", command):
            raise ValueError("Shell operators and compound commands are not supported")
        try:
            tokens = shlex.split(command, posix=(os.name != "nt"))
        except ValueError as exc:
            raise ValueError("Invalid command quoting") from exc
        _validate_command(tokens, root)

        # Handle the portable workspace query without depending on a platform-specific
        # executable (Windows does not ship a `pwd` command).
        if tokens == ["pwd"]:
            return {
                "status": "success",
                "returncode": 0,
                "stdout": f"{root}{os.linesep}",
                "stderr": "",
                "output_truncated": False,
                "duration_ms": 0,
                "cwd": ".",
            }

        # Use the same interpreter running Mosaic for Python validation commands.
        # A bare `python` may resolve to another installation that lacks pytest.
        if tokens[0] == "python":
            tokens[0] = sys.executable

        env = {"PATH": os.environ.get("PATH", ""), "HOME": str(root), "PYTHONNOUSERSITE": "1"}
        for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP"):
            if key in os.environ:
                env[key] = os.environ[key]
        started_at = time.monotonic()
        try:
            process = subprocess.Popen(
                tokens,
                cwd=root,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                start_new_session=(os.name != "nt"),
                creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0),
            )
        except OSError as exc:
            return {
                "status": "launch_failure", "returncode": None, "stdout": "",
                "stderr": str(exc), "duration_ms": round((time.monotonic() - started_at) * 1000),
            }
        stdout_buffer, stderr_buffer = bytearray(), bytearray()
        truncation = {"stdout": False, "stderr": False}
        stdout_thread = threading.Thread(target=_read_capped, args=(process.stdout, stdout_buffer, MAX_PROCESS_OUTPUT_BYTES, truncation, "stdout"), daemon=True)
        stderr_thread = threading.Thread(target=_read_capped, args=(process.stderr, stderr_buffer, MAX_PROCESS_OUTPUT_BYTES, truncation, "stderr"), daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        stop_status = None
        deadline = started_at + COMMAND_TIMEOUT_SECONDS
        while process.poll() is None:
            if cancel_check is not None:
                try:
                    cancellation_requested = cancel_check()
                except Exception:
                    cancellation_requested = True
                if cancellation_requested:
                    stop_status = "cancelled"
                    _stop_process_tree(process)
                    break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                stop_status = "timeout"
                _stop_process_tree(process)
                break
            try:
                process.wait(timeout=min(0.1, remaining))
            except subprocess.TimeoutExpired:
                continue
        if stop_status is not None:
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                _stop_process_tree(process)
                process.wait()
        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)
        if stop_status is not None:
            return {
                "status": stop_status, "returncode": None,
                "stdout": stdout_buffer.decode("utf-8", errors="replace"),
                "stderr": stderr_buffer.decode("utf-8", errors="replace"),
                "output_truncated": truncation["stdout"] or truncation["stderr"],
                "timeout_seconds": COMMAND_TIMEOUT_SECONDS if stop_status == "timeout" else None,
                "duration_ms": round((time.monotonic() - started_at) * 1000),
            }
        return {
            "status": "success" if process.returncode == 0 else "non_zero_exit",
            "returncode": process.returncode,
            "stdout": stdout_buffer.decode("utf-8", errors="replace"),
            "stderr": stderr_buffer.decode("utf-8", errors="replace"),
            "output_truncated": truncation["stdout"] or truncation["stderr"],
            "duration_ms": round((time.monotonic() - started_at) * 1000),
            "cwd": ".",
        }


class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluate a basic arithmetic expression."
    input_schema = {
        "type": "object", "required": ["expression"], "additionalProperties": False,
        "properties": {"expression": {"type": "string", "minLength": 1, "maxLength": 500}},
    }
    permission_policy = {"approval_required": False}

    _operators = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def execute(self, arguments: dict[str, Any], *, workspace: Path | None = None, cancel_check: Callable[[], bool] | None = None) -> Any:
        return {"result": self._evaluate(arguments["expression"])}

    def _evaluate(self, expression: str) -> int | float:
        tree = ast.parse(expression, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 100:
            raise ValueError("Calculator expression is too complex")

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in self._operators:
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                    raise ValueError("Calculator exponent exceeds the safety limit")
                result = self._operators[type(node.op)](left, right)
                if isinstance(result, int) and result.bit_length() > 4096:
                    raise ValueError("Calculator integer result exceeds the safety limit")
                if isinstance(result, float) and not math.isfinite(result):
                    raise ValueError("Calculator result must be finite")
                return result
            if isinstance(node, ast.UnaryOp) and type(node.op) in self._operators:
                return self._operators[type(node.op)](visit(node.operand))
            raise ValueError("Unsupported calculator expression")

        result = visit(tree)
        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Calculator result must be finite")
        return result


class SearchTool(Tool):
    name = "search"
    description = "Search the web using a public search endpoint."
    input_schema = {
        "type": "object", "required": ["query"], "additionalProperties": False,
        "properties": {"query": {"type": "string", "minLength": 1, "maxLength": 500}},
    }
    permission_policy = {"approval_required": True, "scope": "public_web"}

    def execute(self, arguments: dict[str, Any], *, workspace: Path | None = None, cancel_check: Callable[[], bool] | None = None) -> Any:
        retrieved_at = datetime.now(timezone.utc).isoformat()
        url = "https://html.duckduckgo.com/html/?q=" + quote(arguments["query"])
        request = Request(url, headers={"User-Agent": "Mosaic/0.1"})
        try:
            with safe_urlopen(request, timeout=10) as response:
                raw = response.read(1_000_001)
                truncated = len(raw) > 1_000_000
                parser = _SearchResultsParser()
                parser.feed(raw[:1_000_000].decode("utf-8", errors="replace"))
                results_truncated = len(parser.results) > 10
                results = parser.results[:10]
                for index, result in enumerate(results, start=1):
                    result["rank"] = index
                    result["provider"] = "DuckDuckGo"
                    result["retrieved_at"] = retrieved_at
                return {
                    "status": "success" if results else "no_results",
                    "query": arguments["query"],
                    "provider": "DuckDuckGo",
                    "results": results,
                    "retrieved_at": retrieved_at,
                    "truncated": truncated or results_truncated,
                }
        except Exception as exc:
            return {
                "status": "provider_error",
                "query": arguments["query"],
                "provider": "DuckDuckGo",
                "results": [],
                "retrieved_at": retrieved_at,
                "error": f"{type(exc).__name__}: {exc}",
            }


class _SearchResultsParser:
    def __init__(self):
        from html.parser import HTMLParser
        from urllib.parse import parse_qs, unquote, urljoin, urlsplit

        class Parser(HTMLParser):
            def __init__(self, outer):
                super().__init__(convert_charrefs=True)
                self.outer = outer
                self.current = None
                self.capture = None
                self.capture_tag = None

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                classes = set((attrs.get("class") or "").split())
                if tag == "a" and "result__a" in classes:
                    self._finish()
                    href = attrs.get("href", "")
                    href = urljoin("https://html.duckduckgo.com", href)
                    parsed = urlsplit(href)
                    target = parse_qs(parsed.query).get("uddg", [None])[0]
                    if target:
                        href = unquote(target)
                    if urlsplit(href).scheme in {"http", "https"} and urlsplit(href).hostname:
                        self.current = {"title": "", "url": href, "snippet": ""}
                        self.capture = "title"
                        self.capture_tag = "a"
                elif self.current is not None and "result__snippet" in classes:
                    self.capture = "snippet"
                    self.capture_tag = tag

            def handle_data(self, data):
                if self.current is not None and self.capture in {"title", "snippet"}:
                    piece = " ".join(data.split())
                    if piece:
                        self.current[self.capture] += (" " if self.current[self.capture] else "") + piece

            def handle_endtag(self, tag):
                if self.capture_tag == tag:
                    self.capture = None
                    self.capture_tag = None

            def _finish(self):
                if self.current and self.current["title"].strip():
                    self.outer.results.append({
                        "title": self.current["title"].strip()[:300],
                        "url": self.current["url"],
                        "snippet": self.current["snippet"].strip()[:500],
                    })
                self.current = None
                self.capture = None
                self.capture_tag = None

            def close(self):
                super().close()
                self._finish()

        self.results = []
        self.parser = Parser(self)

    def feed(self, content: str) -> None:
        self.parser.feed(content)
        self.parser.close()


class WeatherTool(Tool):
    name = "weather"
    description = "Retrieve current weather for a latitude and longitude."
    input_schema = {
        "type": "object", "required": ["latitude", "longitude"], "additionalProperties": False,
        "properties": {
            "latitude": {"type": "number", "minimum": -90, "maximum": 90},
            "longitude": {"type": "number", "minimum": -180, "maximum": 180},
        },
    }
    permission_policy = {"approval_required": True, "scope": "public_web"}

    def execute(self, arguments: dict[str, Any], *, workspace: Path | None = None, cancel_check: Callable[[], bool] | None = None) -> Any:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={arguments['latitude']}&longitude={arguments['longitude']}"
            "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        )
        with safe_urlopen(url, timeout=10) as response:
            return json.loads(response.read(500_001).decode("utf-8"))



class _ReadableHTML:
    """Small standard-library HTML extractor; scripts and styles are discarded."""

    def __init__(self):
        from html.parser import HTMLParser

        class Parser(HTMLParser):
            def __init__(self, outer):
                super().__init__(convert_charrefs=True)
                self.outer = outer
                self.skip_depth = 0
                self.in_title = False

            def handle_starttag(self, tag, attrs):
                tag = tag.lower()
                if tag in {"script", "style", "noscript", "svg"}:
                    self.skip_depth += 1
                if tag == "title":
                    self.in_title = True

            def handle_endtag(self, tag):
                tag = tag.lower()
                if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
                    self.skip_depth -= 1
                if tag == "title":
                    self.in_title = False

            def handle_data(self, data):
                if self.skip_depth:
                    return
                text = " ".join(data.split())
                if not text:
                    return
                if self.in_title and not self.outer.title:
                    self.outer.title = text[:300]
                self.outer.parts.append(text)

        self.title = ""
        self.parts = []
        self.parser = Parser(self)

    def feed(self, content: str) -> None:
        self.parser.feed(content)


class WebFetchTool(Tool):
    name = "web_fetch"
    description = "Read a public HTTP/HTTPS page as bounded text; private and local destinations are blocked."
    input_schema = {
        "type": "object", "required": ["url"], "additionalProperties": False,
        "properties": {"url": {"type": "string", "minLength": 8, "maxLength": 2048}},
    }
    permission_policy = {"approval_required": True, "scope": "public_web", "timeout_seconds": 10}

    def execute(self, arguments: dict[str, Any], *, workspace: Path | None = None, cancel_check: Callable[[], bool] | None = None) -> Any:
        request = Request(arguments["url"], headers={"User-Agent": "Mosaic/0.1"})
        with safe_urlopen(request, timeout=10) as response:
            content_type = response.headers.get_content_type().lower()
            if content_type not in {"text/html", "text/plain", "application/xhtml+xml"}:
                raise ValueError(f"Unsupported page content type: {content_type}")
            raw = response.read(1_000_001)
            truncated = len(raw) > 1_000_000
            text = raw[:1_000_000].decode(response.headers.get_content_charset() or "utf-8", errors="replace")
            if content_type == "text/plain":
                title = response.geturl()
                content = text
            else:
                parser = _ReadableHTML()
                parser.feed(text)
                title = parser.title or response.geturl()
                content = "\n".join(parser.parts)
            return {
                "url": response.geturl(),
                "title": title[:300],
                "content_type": content_type,
                "content": content[:100_000],
                "truncated": truncated or len(content) > 100_000,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

def register_builtin_tools() -> None:
    from app.tools.registry import registry
    for tool in (FilesystemTool(), TerminalTool(), SearchTool(), WebFetchTool(), CalculatorTool(), WeatherTool()):
        if registry.get(tool.name) is None:
            registry.register(tool)
