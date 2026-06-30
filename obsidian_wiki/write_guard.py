"""Deterministic dry-run evaluator for the wiki-write-guard contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


APPROVED_CLASS_1_PREFIXES = (
    "wiki-export/",
    "_staging/reports/",
    "_insights.md",
    "_meta/",
    "staging/",
    "reviews/",
    "raw/",
)
APPROVED_CLASS_2_PREFIXES = ("_raw/", "_staging/", "staging/", "inbox/", ".memvault/queue/")
REQUIRED_STAGING_METADATA_FIELDS = {
    "title",
    "tags",
    "sources",
    "summary",
    "created",
    "updated",
    "keywords",
}
HIGH_RISK_WRITE_TYPES = {
    "canonical_promotion",
    "delete",
    "move",
    "rebuild",
    "restore",
    "setup",
    "config_update",
    "commit",
    "push",
    "publish",
    "install",
}
CLASS_3_WRITE_TYPES = {
    "link_fix",
    "frontmatter_fix",
    "manifest_update",
    "index_update",
    "log_update",
    "hot_update",
    "generated_block_refresh",
}


@dataclass(frozen=True)
class GuardDecision:
    decision: str
    reason: str
    allowed_to_write_target: bool
    required_action: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "allowed_to_write_target": self.allowed_to_write_target,
            "required_action": self.required_action,
        }


@dataclass(frozen=True)
class GuardedWriteResult:
    decision: GuardDecision
    wrote: bool
    target_path: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.as_dict(),
            "wrote": self.wrote,
            "target_path": self.target_path,
        }


def evaluate_operation(operation: Mapping[str, Any]) -> GuardDecision:
    """Return the dry-run guard decision for a proposed wiki write operation."""
    operation_class = str(operation.get("operation_class", "unknown")).lower()
    write_type = str(operation.get("write_type", "other")).lower()

    if write_type in HIGH_RISK_WRITE_TYPES or _truthy(operation, "deletes", "moves", "renames"):
        return _escalate("high-risk write type or destructive file operation")

    if _truthy(operation, "new_root_schema", "rewrites_many_files", "changes_credentials"):
        return _escalate("broad, credential, or root-schema change")

    if operation_class == "class_5":
        return _escalate("Class 5 dangerous write")

    if operation_class == "class_4":
        return _escalate("Class 4 canonical knowledge write")

    if _truthy(operation, "touches_canonical") and _truthy(operation, "semantic_change"):
        return _escalate("semantic change to canonical content")

    if operation_class == "class_1":
        return _evaluate_class_1(operation)

    if operation_class == "class_2":
        return _evaluate_class_2(operation)

    if operation_class == "class_3":
        return _evaluate_class_3(operation)

    return GuardDecision(
        "queue",
        "unknown or underspecified routine write",
        False,
        "write only a review-queue item; do not write target files",
    )


def _evaluate_class_1(operation: Mapping[str, Any]) -> GuardDecision:
    targets = _target_paths(operation)
    if not targets or not all(_has_allowed_prefix(path, APPROVED_CLASS_1_PREFIXES) for path in targets):
        return _queue("Class 1 target is not an approved generated/report location")
    if _truthy(operation, "overwrites_human_authored", "promotes_claims"):
        return _escalate("generated report would overwrite human-authored or canonical truth")
    return _approve("generated or rebuildable report output")


def _evaluate_class_2(operation: Mapping[str, Any]) -> GuardDecision:
    targets = _target_paths(operation)
    if not targets or not all(_has_allowed_prefix(path, APPROVED_CLASS_2_PREFIXES) for path in targets):
        return _queue("Class 2 target is not an approved staging/candidate location")
    if not _truthy(operation, "metadata_present"):
        return _queue("staging candidate lacks required metadata")
    metadata_fields = _metadata_fields(operation)
    if not metadata_fields:
        return _queue("staging candidate must list metadata_fields")
    if not REQUIRED_STAGING_METADATA_FIELDS.issubset(metadata_fields):
        missing = sorted(REQUIRED_STAGING_METADATA_FIELDS - metadata_fields)
        return _queue(f"staging candidate lacks required metadata fields: {', '.join(missing)}")
    if not ({"category", "type"} & metadata_fields):
        return _queue("staging candidate lacks required metadata fields: category or type")
    return _approve("staging candidate is isolated from canonical truth")


def _evaluate_class_3(operation: Mapping[str, Any]) -> GuardDecision:
    targets = _target_paths(operation)
    if not targets:
        return _queue("Class 3 change must name target paths")
    if str(operation.get("write_type", "")).lower() not in CLASS_3_WRITE_TYPES:
        return _queue("Class 3 change must use an explicit mechanical write type")
    if not (operation.get("source_refs") or operation.get("source_absence_reason")):
        return _queue("Class 3 change must include source refs or explain why no source exists")
    if not _truthy(operation, "mechanical_change", "append_only"):
        return _queue("Class 3 change must prove it is mechanical or append-only")
    if int(operation.get("changed_files", 0) or 0) > 3:
        return _queue("Class 3 change touches more than 3 files")
    if int(operation.get("changed_lines", 0) or 0) > 80:
        return _queue("Class 3 change exceeds 80 changed lines")
    if _truthy(operation, "semantic_change", "policy_change", "architecture_change", "boundary_change"):
        return _escalate("Class 3 candidate changes meaning or policy")
    if str(operation.get("write_type", "")).lower() == "log_update":
        if not _truthy(operation, "append_only"):
            return _queue("log telemetry must be append-only")
        if int(operation.get("append_lines", 0) or 0) != 1:
            return _queue("log telemetry must be exactly one bounded append line")
        if _truthy(operation, "semantic_claim"):
            return _escalate("log telemetry contains a semantic claim")
    return _approve("small mechanical maintenance")


def _approve(reason: str) -> GuardDecision:
    return GuardDecision("approve", reason, True, "writer may continue unattended")


def _queue(reason: str) -> GuardDecision:
    return GuardDecision(
        "queue",
        reason,
        False,
        "write only a review-queue item; do not write target files",
    )


def _escalate(reason: str) -> GuardDecision:
    return GuardDecision(
        "escalate",
        reason,
        False,
        "do not write target files; human or designated reviewer decision required",
    )


def _truthy(operation: Mapping[str, Any], *keys: str) -> bool:
    return any(bool(operation.get(key)) for key in keys)


def _target_paths(operation: Mapping[str, Any]) -> list[str]:
    raw = operation.get("target_paths", [])
    if isinstance(raw, str):
        return [raw]
    return [str(path) for path in raw]


def _metadata_fields(operation: Mapping[str, Any]) -> set[str]:
    raw = operation.get("metadata_fields", [])
    if isinstance(raw, str):
        return {raw}
    return {str(field) for field in raw}


def _has_allowed_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    normalized = path.strip().lstrip("./")
    return any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in prefixes)


def guarded_append_log_line(vault_path: Path, operation: Mapping[str, Any], line: str) -> GuardedWriteResult:
    """Append one log line to a vault only when the write guard approves it."""
    decision = evaluate_operation(operation)
    target = vault_path / "log.md"
    if decision.decision != "approve" or not _is_exact_log_append_operation(operation) or "\n" in line:
        return GuardedWriteResult(decision=decision, wrote=False, target_path=str(target))

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(line.rstrip("\n") + "\n")
    return GuardedWriteResult(decision=decision, wrote=True, target_path=str(target))


def _is_exact_log_append_operation(operation: Mapping[str, Any]) -> bool:
    return (
        str(operation.get("write_type", "")).lower() == "log_update"
        and _target_paths(operation) == ["log.md"]
        and operation.get("append_only") is True
        and int(operation.get("append_lines", 0) or 0) == 1
    )


DRY_RUN_SCENARIOS: dict[str, dict[str, Any]] = {
    "safe-log": {
        "operation_class": "class_3",
        "write_type": "log_update",
        "target_paths": ["log.md"],
        "changed_files": 1,
        "changed_lines": 1,
        "append_only": True,
        "append_lines": 1,
        "semantic_claim": False,
        "source_absence_reason": "runtime telemetry event",
    },
    "canonical-promotion": {
        "operation_class": "class_4",
        "write_type": "canonical_promotion",
        "target_paths": ["wiki/example.md"],
        "touches_canonical": True,
        "semantic_change": True,
    },
    "dangerous-delete": {
        "operation_class": "class_5",
        "write_type": "delete",
        "target_paths": ["wiki/example.md"],
        "deletes": True,
    },
    "unknown-routine": {
        "operation_class": "unknown",
        "write_type": "other",
        "target_paths": ["wiki/example.md"],
    },
}
