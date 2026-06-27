---
name: wiki-history-ingest
description: >
  Unified wiki-history-ingest entrypoint for conversation/session sources. Use this when the user says
  "/wiki-history-ingest claude" or "/wiki-history-ingest codex", or asks to ingest agent history without
  naming the underlying skill. This router dispatches to the specialized history skill.
---

# Unified History Ingest Router

This is a thin router for **history sources only**. It does not replace `wiki-ingest` for documents.

## Write Guard

This router must not bypass `wiki-write-guard`. When dispatching to a
destination history skill, forward the intended mode and require the destination
skill to run the guard before any write. If the destination skill cannot produce
a guard result, it may only inventory/report and must not write target files.

If the target vault is Alex's Codex memory vault, the guard overrides generic
standalone paths and old destination-skill body steps. Apply destination
instructions only to translated, guard-approved target paths.

## Subcommands

If the user invokes `/wiki-history-ingest <target>` (or equivalent text command), dispatch directly:

| Subcommand | Route To |
|---|---|
| `claude` | `claude-history-ingest` |
| `codex` | `codex-history-ingest` |
| `hermes` | `hermes-history-ingest` |
| `openclaw` | `openclaw-history-ingest` |
| `auto` | infer from context using rules below |

## Routing Rules

1. If the user explicitly says `claude`, `codex`, `hermes`, or `openclaw`, route directly.
2. If the user provides a path/source:
   - `~/.claude` or Claude memory/session JSONL artifacts -> `claude-history-ingest`
   - `~/.codex` or rollout/session index artifacts -> `codex-history-ingest`
   - `~/.hermes` or Hermes memories/session artifacts -> `hermes-history-ingest`
   - `~/.openclaw` or OpenClaw MEMORY.md/session JSONL artifacts -> `openclaw-history-ingest`
3. If ambiguous, ask one short clarification:
   - "Should I ingest `claude`, `codex`, `hermes`, or `openclaw` history?"

## Execution Contract

- After routing, execute the destination skill's workflow exactly.
- Do not duplicate destination logic in this file.
- Leave manifest/index/log update semantics to the destination skill.

## UX Convention

- Use `wiki-ingest` for **documents/content sources**
- Use `wiki-history-ingest` for **agent history sources**

Examples:

- `/wiki-history-ingest claude`
- `/wiki-history-ingest codex`
- `/wiki-history-ingest hermes`
- `/wiki-history-ingest openclaw`
- `$wiki-history-ingest claude` (agents that use `$skill` invocation)
