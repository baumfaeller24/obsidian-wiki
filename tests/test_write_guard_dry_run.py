from __future__ import annotations

import json
import tempfile
from pathlib import Path

from obsidian_wiki.cli import main
from obsidian_wiki.write_guard import evaluate_operation


def test_safe_log_telemetry_is_approved() -> None:
    decision = evaluate_operation(
        {
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
    )

    assert decision.decision == "approve"
    assert decision.allowed_to_write_target is True


def test_canonical_promotion_escalates() -> None:
    decision = evaluate_operation(
        {
            "operation_class": "class_4",
            "write_type": "canonical_promotion",
            "target_paths": ["wiki/example.md"],
            "touches_canonical": True,
            "semantic_change": True,
        }
    )

    assert decision.decision == "escalate"
    assert decision.allowed_to_write_target is False


def test_unknown_write_is_queued_not_approved() -> None:
    decision = evaluate_operation(
        {
            "operation_class": "unknown",
            "write_type": "other",
            "target_paths": ["wiki/example.md"],
        }
    )

    assert decision.decision == "queue"
    assert decision.allowed_to_write_target is False


def test_log_telemetry_with_semantic_claim_escalates() -> None:
    decision = evaluate_operation(
        {
            "operation_class": "class_3",
            "write_type": "log_update",
            "target_paths": ["log.md"],
            "changed_files": 1,
            "changed_lines": 1,
            "append_only": True,
            "append_lines": 1,
            "semantic_claim": True,
            "source_absence_reason": "runtime telemetry event",
        }
    )

    assert decision.decision == "escalate"


def test_underspecified_class_3_is_queued_not_approved() -> None:
    decision = evaluate_operation({"operation_class": "class_3"})

    assert decision.decision == "queue"
    assert decision.allowed_to_write_target is False


def test_guard_dry_run_cli_builtin_json_output(capsys) -> None:
    exit_code = main(["guard-dry-run", "--scenario", "safe-log", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert payload[0]["scenario"] == "safe-log"
    assert payload[0]["decision"] == "approve"


def test_guard_dry_run_cli_operation_json(capsys) -> None:
    operation = {
        "operation_class": "class_5",
        "write_type": "delete",
        "target_paths": ["wiki/example.md"],
        "deletes": True,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "operation.json"
        path.write_text(json.dumps(operation), encoding="utf-8")

        exit_code = main(["guard-dry-run", "--operation-json", str(path), "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload[0]["decision"] == "escalate"
    assert payload[0]["allowed_to_write_target"] is False
