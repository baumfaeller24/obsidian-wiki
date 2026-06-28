from __future__ import annotations

import json
from pathlib import Path

from obsidian_wiki.cli import main


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


def write_operation(tmp_path: Path, operation: dict[str, object]) -> Path:
    path = tmp_path / "operation.json"
    path.write_text(json.dumps(operation), encoding="utf-8")
    return path


def test_guarded_log_append_cli_writes_approved_log_line(tmp_path: Path, capsys) -> None:
    operation_path = write_operation(tmp_path, safe_log_operation())
    vault = tmp_path / "vault"

    exit_code = main(
        [
            "guarded-log-append",
            "--vault",
            str(vault),
            "--operation-json",
            str(operation_path),
            "--line",
            "- [2026-06-28T00:00:00Z] CLI_SAFE ok=true",
            "--format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["wrote"] is True
    assert payload["decision"]["decision"] == "approve"
    assert (vault / "log.md").read_text(encoding="utf-8") == "- [2026-06-28T00:00:00Z] CLI_SAFE ok=true\n"


def test_guarded_log_append_cli_blocks_risky_operation(tmp_path: Path, capsys) -> None:
    operation_path = write_operation(
        tmp_path,
        {
            "operation_class": "class_4",
            "write_type": "canonical_promotion",
            "target_paths": ["wiki/example.md"],
            "touches_canonical": True,
            "semantic_change": True,
        },
    )
    vault = tmp_path / "vault"

    exit_code = main(
        [
            "guarded-log-append",
            "--vault",
            str(vault),
            "--operation-json",
            str(operation_path),
            "--line",
            "- [2026-06-28T00:00:00Z] SHOULD_NOT_WRITE ok=false",
            "--format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 2
    assert payload["wrote"] is False
    assert payload["decision"]["decision"] == "escalate"
    assert not (vault / "log.md").exists()


def test_guarded_log_append_cli_blocks_embedded_newline(tmp_path: Path, capsys) -> None:
    operation_path = write_operation(tmp_path, safe_log_operation())
    vault = tmp_path / "vault"

    exit_code = main(
        [
            "guarded-log-append",
            "--vault",
            str(vault),
            "--operation-json",
            str(operation_path),
            "--line",
            "first\nsecond",
            "--format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 2
    assert payload["wrote"] is False
    assert not (vault / "log.md").exists()


def test_guarded_log_append_cli_blocks_truthy_string_append_only(tmp_path: Path, capsys) -> None:
    operation = safe_log_operation()
    operation["append_only"] = "false"
    operation_path = write_operation(tmp_path, operation)
    vault = tmp_path / "vault"

    exit_code = main(
        [
            "guarded-log-append",
            "--vault",
            str(vault),
            "--operation-json",
            str(operation_path),
            "--line",
            "- [2026-06-28T00:00:00Z] SHOULD_NOT_WRITE ok=false",
            "--format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 2
    assert payload["wrote"] is False
    assert not (vault / "log.md").exists()
