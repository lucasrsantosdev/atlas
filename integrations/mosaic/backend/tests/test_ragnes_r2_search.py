import pytest

from app.context.search import search_workspace_artifacts


def test_lexical_search_returns_relevant_bounded_snippets_with_provenance(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text(
        "Mosaic overview\nThe harness controls tool approval.\nDone.", encoding="utf-8"
    )
    (workspace / "irrelevant.txt").write_text("gardening and cooking", encoding="utf-8")
    (workspace / "backend").mkdir()
    (workspace / "backend" / "approval.py").write_text(
        "def request_approval():\n    return 'pending'\n", encoding="utf-8"
    )

    result = search_workspace_artifacts(workspace, "tool approval")

    assert result["results"]
    assert result["results"][0]["path"] == "backend/approval.py"
    assert result["results"][0]["snippets"][0]["start_line"] >= 1
    assert "approval" in result["results"][0]["matched_terms"]
    assert "gardening" not in str(result["results"])


def test_lexical_search_finds_terms_beyond_first_excerpt_window(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    lines = [f"ordinary line {index}" for index in range(250)]
    lines[231] = "unique retrieval identifier"
    (workspace / "large.txt").write_text("\n".join(lines), encoding="utf-8")

    result = search_workspace_artifacts(workspace, "unique retrieval identifier")

    match = next(item for item in result["results"] if item["path"] == "large.txt")
    assert any(snippet["matched_line"] == 232 for snippet in match["snippets"])


def test_lexical_search_is_deterministic_and_respects_result_limits(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for name in ("a.txt", "b.txt", "c.txt"):
        (workspace / name).write_text("common marker", encoding="utf-8")

    first = search_workspace_artifacts(workspace, "common marker", max_results=2)
    second = search_workspace_artifacts(workspace, "common marker", max_results=2)

    assert [item["path"] for item in first["results"]] == ["a.txt", "b.txt"]
    assert first == second
    assert first["truncated"] is True


def test_lexical_search_rejects_invalid_limits_and_empty_queries(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "a.txt").write_text("anything", encoding="utf-8")

    assert search_workspace_artifacts(workspace, "the and de")["results"] == []
    with pytest.raises(ValueError):
        search_workspace_artifacts(workspace, "anything", max_results=11)


def test_lexical_search_skips_symlinks_and_oversized_files(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("unique secretterm", encoding="utf-8")
    try:
        (workspace / "link.txt").symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks are not supported in this environment")
    (workspace / "large.txt").write_text("secretterm" * 110_000, encoding="utf-8")

    result = search_workspace_artifacts(workspace, "secretterm")

    assert all(item["path"] not in {"link.txt", "large.txt"} for item in result["results"])
