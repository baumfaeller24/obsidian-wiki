---
name: wiki-quick-chat-capture
description: >
  Fast, zero-friction capture of technical findings from the current conversation to the wiki's
  _raw/ staging area. Use this skill when the user says "/wiki-quick-chat-capture", "quick capture",
  "capture this finding", "save this bug fix", "capture this gotcha", "drop this to raw",
  "quick save to wiki", or wants to capture a non-obvious discovery mid-session without a full
  wiki-ingest run. Writes one _raw/ file per topic cluster in under 60 seconds — no subagents,
  no QMD updates, no manifest writes. Run /wiki-ingest or /data-ingest later to promote raw
  files to proper wiki pages.
---

# Wiki Quick Chat Capture

Extract reusable technical findings from the current conversation and stage them in `_raw/` for
later promotion. The goal is zero-friction capture of discoveries that would otherwise be lost
when the session ends.

## When to Use This Skill

This is the right tool when:
- The user just hit a non-obvious bug or confirmed a framework gotcha mid-session
- There's a concrete finding worth keeping but a full `/wiki-ingest` run would be too disruptive
- The user wants to offload the knowledge now and defer promotion to end-of-day

It is NOT a replacement for `wiki-capture` (which promotes directly to a final wiki page) or
`wiki-ingest` (which handles full document ingestion with cross-links and manifest tracking).

## Before You Start

1. **Resolve config** — follow the Config Resolution Protocol in `llm-wiki/SKILL.md` (walk up
   CWD for `.env` → `~/.obsidian-wiki/config` → prompt setup). This gives `OBSIDIAN_VAULT_PATH`.
2. Ensure `$OBSIDIAN_VAULT_PATH/_raw/` exists. If not, create it.

## Step 1: Scan the Conversation for Findings

Read the current conversation and extract **reusable technical findings** — knowledge that would
be valuable in 3 months with no memory of this chat.

**Worth capturing:**
- Non-obvious bugs and their root causes
- Framework or library gotchas (undocumented behavior, edge cases)
- API behavior that surprised the user
- Workarounds or fixes that required investigation
- Environment/toolchain quirks
- Patterns that emerged from debugging or testing

**Skip:**
- Greetings, logistics, meta-conversation
- Exploratory back-and-forth where no conclusion was reached
- Things already known or obvious from documentation
- Content the user has already saved elsewhere

If nothing material emerged, tell the user and stop.

## Step 2: Cluster by Topic

Group related findings under a single topic. One cluster → one raw file.

- If a single bug was investigated, that's one cluster
- If two unrelated API gotchas came up, those are two clusters
- If a sequence of related fixes all point to the same root cause, that's one cluster

Name each cluster with a brief slug: `swift-actor-reentrancy`, `nextjs-hydration-mismatch`,
`postgres-advisory-locks`, etc.

## Step 3: Infer Project Context

Check the conversation for clues about the active project: repository names, file paths,
framework mentions, error messages. Use the most specific project name you can reliably infer.
If unclear, use `null`.

## Step 4: Write Raw Files

For each cluster, write a file to `$OBSIDIAN_VAULT_PATH/_raw/YYYY-MM-DD-<slug>.md` using
today's date. Use the format below exactly — it is designed to be compatible with `wiki-ingest`
and `data-ingest` for seamless promotion.

```yaml
---
title: "<descriptive title>"
category: skills
tags: [<2-4 domain tags matching the vault taxonomy>]
summary: "<1-2 sentences, ≤200 chars — what is the finding?>""
tier: supporting
related: []
extends: null
contradicts: null
superseded_by: null
capture_source: claude-session
project: <project-name or null>
base_confidence: <0.6-0.9 based on how clearly confirmed the finding was>
lifecycle: draft
lifecycle_changed: <ISO date today>
provenance:
  extracted: <0.0-1.0 — how much was stated directly in the session>
  inferred: <0.0-1.0 — how much was synthesized or generalized>
sources:
  - "claude-session <ISO date today>"
---
```

**Calibrating `base_confidence`:**
- 0.6 — finding was discussed but not fully confirmed
- 0.75 — fix was applied and appeared to work in the session
- 0.9 — finding was confirmed with a reproducible test or clear evidence

**Body structure** — use the finding block format:

```markdown
# <Title>

## Problem
<What went wrong or what was surprising — be specific about the symptom>

## Root Cause
<Why it happened — the underlying mechanism, not just the surface error>

## Fix
<What resolved it — commands, code patterns, config changes>

## Confirmed By
<How the fix was validated — test passed, behavior changed, error disappeared>

## Notes
<Caveats, related edge cases, follow-up questions — omit if none>
```

If the finding is a "gotcha" rather than a bug/fix, adapt freely:
- **Gotcha** → use "Behavior" instead of "Problem", "Explanation" instead of "Root Cause",
  "Workaround / Pattern" instead of "Fix"

Apply provenance markers per the `llm-wiki` convention:
- No marker — explicitly stated in the conversation
- `^[inferred]` — synthesized or generalized beyond what was explicitly said
- `^[ambiguous]` — uncertain or potentially incomplete

## Step 5: Confirm to User

Report what was written, one line per file:

```
Staged to _raw/:
  _raw/2026-05-27-swift-actor-reentrancy.md  — "Actor reentrancy causes deadlock in async forEach"
  _raw/2026-05-27-xcode-derived-data-cache.md — "Stale derived data silently breaks incremental builds"

Run /wiki-ingest (or /data-ingest) to promote these to full wiki pages.
```

If nothing was captured, say: "Nothing worth capturing found in this session."

## What This Skill Does NOT Do

- No manifest writes — `_raw/` files are not tracked in `.manifest.json`
- No `index.md` or `log.md` updates — those happen during promotion
- No `hot.md` update — not a full write operation
- No QMD refresh — raw files are drafts, not indexed content
- No subagents — everything runs inline, in this context window

These are intentional constraints. The whole point is speed. Promotion via `/wiki-ingest` handles
all of the above when the user is ready.
