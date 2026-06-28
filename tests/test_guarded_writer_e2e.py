from __future__ import annotations

from pathlib import Path

from obsidian_wiki.write_guard import guarded_append_log_line


def safe_log_operation() -> dict[str, object]:
    return {
        "operation_class": "class_3",
        "write_type": "log_update",
        "target_paths": ["log.md"],
        "changed_files": 1,
        "changed_lines": 1,
        "append_only": True,
        "append_lines": 1,
        "semantic_claim": False,
        "source_absence_reason": "runtime telemetry event",
    }


def risky_canonical_operation() -> dict[str, object]:
    return {
        "operation_class": "class_4",
        "write_type": "canonical_promotion",
        "target_paths": ["wiki/example.md"],
        "touches_canonical": True,
        "semantic_change": True,
    }


def approved_non_log_operation() -> dict[str, object]:
    return {
        "operation_class": "class_2",
        "write_type": "staging_candidate",
        "target_paths": ["_staging/example.md"],
        "metadata_present": True,
    }


def test_guarded_writer_appends_safe_log_line_to_temp_vault(tmp_path: Path) -> None:
    result = guarded_append_log_line(
        tmp_path,
        safe_log_operation(),
        "- [2026-06-28T00:00:00Z] SAFE_LOG_TEST ok=true",
    )

    assert result.decision.decision == "approve"
    assert result.wrote is True
    assert (tmp_path / "log.md").read_text(encoding="utf-8") == (
        "- [2026-06-28T00:00:00Z] SAFE_LOG_TEST ok=true\n"
    )


def test_guarded_writer_blocks_risky_write_and_leaves_temp_vault_untouched(tmp_path: Path) -> None:
    result = guarded_append_log_line(
        tmp_path,
        risky_canonical_operation(),
        "- [2026-06-28T00:00:00Z] SHOULD_NOT_WRITE ok=false",
    )

    assert result.decision.decision == "escalate"
    assert result.wrote is False
    assert not (tmp_path / "log.md").exists()


def test_guarded_writer_rejects_approved_non_log_operation_for_log_append(tmp_path: Path) -> None:
    result = guarded_append_log_line(
        tmp_path,
        approved_non_log_operation(),
        "- [2026-06-28T00:00:00Z] SHOULD_NOT_WRITE ok=false",
    )

    assert result.decision.decision == "approve"
    assert result.wrote is False
    assert not (tmp_path / "log.md").exists()


def test_guarded_writer_rejects_embedded_newline_log_payload(tmp_path: Path) -> None:
    result = guarded_append_log_line(
        tmp_path,
        safe_log_operation(),
        "- [2026-06-28T00:00:00Z] FIRST\n- [2026-06-28T00:00:01Z] SECOND",
    )

    assert result.decision.decision == "approve"
    assert result.wrote is False
    assert not (tmp_path / "log.md").exists()


def test_guarded_writer_rejects_truthy_string_append_only(tmp_path: Path) -> None:
    operation = safe_log_operation()
    operation["append_only"] = "false"

    result = guarded_append_log_line(
        tmp_path,
        operation,
        "- [2026-06-28T00:00:00Z] SHOULD_NOT_WRITE ok=false",
    )

    assert result.decision.decision == "approve"
    assert result.wrote is False
    assert not (tmp_path / "log.md").exists()
