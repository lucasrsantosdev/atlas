import pytest

from app.context.artifacts import (
    MAX_ARTIFACT_BYTES,
    list_workspace_artifacts,
    read_workspace_excerpt,
)


def test_inventory_lists_bounded_metadata_without_reading_contents(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("secret body should not be returned", encoding="utf-8")
    nested = workspace / "backend"
    nested.mkdir()
    (nested / "main.py").write_text("print('ok')", encoding="utf-8")
    (workspace / ".git").mkdir()
    (workspace / ".git" / "config").write_text("internal git data", encoding="utf-8")

    result = list_workspace_artifacts(workspace)

    assert result["count"] == 2
    assert [entry["path"] for entry in result["entries"]] == ["README.md", "backend/main.py"]
    assert all("content" not in entry for entry in result["entries"])
    assert all("secret body" not in str(entry) for entry in result["entries"])


def test_inventory_reports_truncation_and_rejects_invalid_limits(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for index in range(3):
        (workspace / f"{index}.txt").write_text(str(index), encoding="utf-8")

    result = list_workspace_artifacts(workspace, max_entries=2)

    assert result["count"] == 2
    assert result["truncated"] is True
    with pytest.raises(ValueError):
        list_workspace_artifacts(workspace, max_entries=MAX_ARTIFACT_BYTES)


def test_direct_read_returns_bounded_excerpt_with_line_provenance(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "notes.md").write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")

    result = read_workspace_excerpt(workspace, "notes.md", start_line=2, max_lines=2)

    assert result["path"] == "notes.md"
    assert result["start_line"] == 2
    assert result["end_line"] == 3
    assert result["content"] == "two\nthree"
    assert result["truncated"] is True
    assert result["total_lines"] == 4


@pytest.mark.parametrize("path", ["../outside.txt", "/etc/passwd", "missing.txt"])
def test_direct_read_rejects_unsafe_or_missing_paths(tmp_path, path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    with pytest.raises(ValueError):
        read_workspace_excerpt(workspace, path)


def test_direct_read_rejects_symlink_escape(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("do not read", encoding="utf-8")
    try:
        (workspace / "external.txt").symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks are not supported in this environment")

    with pytest.raises(ValueError, match="Symlink"):
        read_workspace_excerpt(workspace, "external.txt")


def test_direct_read_rejects_oversized_and_binary_files(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "large.txt").write_bytes(b"x" * (MAX_ARTIFACT_BYTES + 1))
    (workspace / "binary.bin").write_bytes(b"\xff\xfe\x00")

    with pytest.raises(ValueError, match="direct-read limit"):
        read_workspace_excerpt(workspace, "large.txt")
    with pytest.raises(ValueError, match="UTF-8"):
        read_workspace_excerpt(workspace, "binary.bin")
