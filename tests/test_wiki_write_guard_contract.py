from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".skills"


EXPECTED_GUARDED_SKILLS = {
    "claude-history-ingest",
    "codex-history-ingest",
    "copilot-history-ingest",
    "cross-linker",
    "daily-update",
    "graph-colorize",
    "hermes-history-ingest",
    "memory-bridge",
    "openclaw-history-ingest",
    "pi-history-ingest",
    "tag-taxonomy",
    "wiki-agent",
    "wiki-capture",
    "wiki-context-pack",
    "wiki-dashboard",
    "wiki-dedup",
    "wiki-digest",
    "wiki-export",
    "wiki-import",
    "wiki-ingest",
    "wiki-lint",
    "wiki-query",
    "wiki-rebuild",
    "wiki-research",
    "wiki-setup",
    "wiki-stage-commit",
    "wiki-status",
    "wiki-switch",
    "wiki-synthesize",
    "wiki-update",
}

ALIAS_SKILLS = {
    "data-ingest",
    "ingest-url",
    "obsidian-wiki-ingest",
}


def skill_text(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def test_write_guard_blocks_canonical_and_dangerous_unattended_writes() -> None:
    text = skill_text("wiki-write-guard")

    for required in [
        "Return exactly one decision",
        "`approve`",
        "`queue`",
        "`reject`",
        "`escalate`",
        "Class 4: Canonical Knowledge Writes",
        "Class 5: Dangerous Writes",
        "Do not approve unattended. Return `escalate`.",
        "Do not approve unattended. Return `escalate` or `reject`.",
        "If a writer wants to commit or push, return `escalate`.",
    ]:
        assert required in text


def test_read_only_telemetry_is_guarded_but_can_run_without_human_input() -> None:
    text = skill_text("wiki-write-guard")

    for required in [
        "append-only `log.md` telemetry",
        "read-only query/report operation",
        "contains no new semantic claim",
        "exactly one bounded append line",
    ]:
        assert required in text


def test_machine_preflight_is_documented_for_unattended_writes() -> None:
    text = skill_text("wiki-write-guard")

    for required in [
        "## Machine Preflight",
        "python -m obsidian_wiki guard-dry-run",
        "--operation-json",
        "--fail-on-non-approve",
        "Continue to the target write only when the JSON decision is `approve`",
        "Do not claim that an automated write path has been verified unless this preflight ran.",
    ]:
        assert compact(required) in compact(text)


def test_non_paper_pages_require_machine_readable_metadata_header() -> None:
    for name in ["llm-wiki", "wiki-ingest", "wiki-update", "wiki-capture"]:
        text = skill_text(name)
        for required in ["created", "updated", "summary", "keywords"]:
            assert required in text
        assert "frontmatter is the" in text.lower()


def test_raw_capture_format_has_machine_readable_metadata_header() -> None:
    text = (SKILLS / "wiki-capture" / "references" / "RAW-FORMAT.md").read_text(encoding="utf-8")

    for required in ["created", "updated", "summary", "keywords"]:
        assert required in text
    assert "frontmatter is the machine-readable header" in text.lower()


def test_staging_guard_requires_summary_and_keywords_metadata() -> None:
    text = skill_text("wiki-write-guard")

    for required in ["`summary`", "`keywords`", "`created`", "`updated`", "`metadata_fields`"]:
        assert required in text


def test_write_capable_skills_reference_the_write_guard() -> None:
    missing = []
    for name in sorted(EXPECTED_GUARDED_SKILLS):
        text = skill_text(name)
        if "wiki-write-guard" not in text:
            missing.append(name)

    assert missing == []


def test_alias_skills_route_to_the_guarded_ingest_skill() -> None:
    missing = []
    for name in sorted(ALIAS_SKILLS):
        text = skill_text(name)
        if "wiki-ingest" not in text or "Write Guard section" not in text:
            missing.append(name)

    assert missing == []


def test_log_and_report_writers_have_explicit_guard_before_write() -> None:
    checks = {
        "wiki-status": ["`_insights.md`", "`log.md`", "`approve`", "`reject`", "`escalate`"],
        "wiki-query": ["Step 6 `log.md` append", "without writing the log line"],
        "wiki-context-pack": ["optional Step 6 append to `log.md`", "without writing the log line"],
        "memory-bridge": ["Step 4 append to `log.md`", "without writing the log line"],
    }

    for name, required_phrases in checks.items():
        text = skill_text(name)
        guard_index = text.index("## Write Guard")
        next_section_index = text.index("\n## ", guard_index + 1)
        guard_section = text[guard_index:next_section_index]
        later_text = text[next_section_index:].lower()

        assert "append to" in later_text
        assert "wiki-write-guard" in guard_section
        compact_guard_section = compact(guard_section)
        for phrase in required_phrases:
            assert compact(phrase) in compact_guard_section
