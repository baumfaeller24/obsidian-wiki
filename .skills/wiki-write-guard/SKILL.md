---
name: wiki-write-guard
description: >
  Automated write checker for Obsidian wiki operations. Use this skill before any wiki skill writes,
  moves, deletes, promotes, imports, rebuilds, stages, updates manifest/index/log/hot files, creates
  generated reports, or changes canonical memory. It classifies the proposed write, checks target
  paths and source metadata, approves safe unattended writes, queues unclear routine work, and
  escalates risky work.
---

# Wiki Write Guard - Automated Write Checker

You are the checker in a writer/checker workflow. You do not distill knowledge
and you do not invent content. You classify a proposed write and decide whether
the writer may continue unattended.

This guard exists so routine memory upkeep can run without the human operator
being present, while canonical truth, agent boundaries, and destructive actions
stay protected.

## Required Input

Before any write, the writer must prepare a proposed operation with:

- `operation_class`: one of `class_1`, `class_2`, `class_3`, `class_4`,
  `class_5`, or `unknown`
- `source_agent`: `codex`, `claude`, `copilot`, `hermes`, `openclaw`, `pi`,
  `human`, `external`, or `unknown`
- `vault_path`
- `target_paths`
- `source_refs` or `source_absence_reason`
- `scope`
- `write_type`: report, quick_capture, staging_candidate, staged_promotion,
  manifest_update, index_update, log_update, hot_update, dashboard_update,
  link_fix, frontmatter_fix, canonical_promotion, import, export, delete,
  move, rebuild, restore, setup, config_update, or other
- `planned_diff_summary`: files and expected changed lines when known
- whether the operation touches canonical directories
- whether it deletes, renames, moves, rewrites many files, imports external
  truth, or creates a new root directory

If the writer has not prepared this, build the proposed operation from the
writer's stated plan, then check it before any file write.

## Machine Preflight

For unattended or automated writer runs, run the deterministic CLI preflight
before applying any target write.

1. Write the proposed operation as JSON to a temporary file outside the vault,
   for example `/tmp/wiki-write-operation.json`.
2. Run:
   ```bash
   python -m obsidian_wiki guard-dry-run \
     --operation-json /tmp/wiki-write-operation.json \
     --format json \
     --fail-on-non-approve
   ```
3. Continue to the target write only when the JSON decision is `approve` and the
   command exits `0`.
4. On `queue`, write only the review-queue item; do not write the original
   target.
5. On `reject` or `escalate`, stop before touching target files.

If the CLI is unavailable, fall back to this skill's semantic decision rules and
treat the result as not machine-verified. Do not claim that an automated write
path has been verified unless this preflight ran.

## Decisions

Return exactly one decision:

- `approve`: writer may continue unattended
- `queue`: do not write the original target; create a review-queue item instead
- `reject`: do not write; the operation is unsafe or out of scope
- `escalate`: do not write; human or designated reviewer decision is required

Use `queue` for unclear routine work. Do not interrupt the human operator for
routine uncertainty.

Use `escalate` for semantic policy, architecture, security, retention,
agent-boundary, canonical-promotion, destructive, broad, or cross-agent-truth
work.

## Write Classes

### Class 1: Generated Reports

Examples:

- inventory report
- orphan/link report
- source coverage report
- status/dashboard output
- review-queue summary
- regenerable graph/status/insights output
- export artifact under an export directory

Approve unattended when:

- output is clearly generated or rebuildable
- target is an approved report/generated/export location
- it does not overwrite human-authored canonical pages
- it does not promote claims into canonical truth

### Class 2: Staging Candidate Writes

Examples:

- `_raw/` quick capture
- `_staging/` page or patch produced by `WIKI_STAGED_WRITES=true`
- candidate memory card
- candidate decision
- conflict card
- source/paper card
- ingest candidate distilled from agent history

Approve unattended when:

- target is an approved staging/candidate location
- metadata is present: `title`, `category` or `type`, `tags`, `sources`,
  `created`, `updated`, `confidence` or `base_confidence` when applicable,
  and explicit `source_agent` when the source is agent history
- candidate cannot be mistaken for canonical truth

### Class 3: Small Mechanical Maintenance

Examples:

- unambiguous wikilink fix
- alias addition
- mechanical frontmatter normalization
- generated block refresh
- manifest/index/log/hot update tied to an approved Class 1, Class 2, or
  eligible Class 3 write
- append-only `log.md` telemetry for a read-only query/report operation,
  when it contains no new semantic claim and does not alter content pages

Approve unattended only when all checks pass:

- maximum 3 files changed
- maximum 80 changed lines
- for read-only query/report telemetry, exactly one bounded append line to
  `log.md`
- no delete
- no rename or move
- no new root schema
- no source-agent mixing
- no semantic rule, architecture, policy, security, retention, or boundary
  change
- no change to claim meaning, decision meaning, or canonical truth

If the operation changes meaning, promote it to Class 4.

### Class 4: Canonical Knowledge Writes

Examples:

- new durable rule
- architecture decision
- update to a canonical knowledge claim
- staging-to-canonical promotion
- conflict resolution
- import into live canonical pages
- cross-agent memory consolidation

Do not approve unattended. Return `escalate`.

If `WIKI_STAGED_WRITES=true`, writing a proposed canonical page into `_staging/`
is Class 2. Promoting it from `_staging/` to the live wiki remains Class 4 and
must not be modeled as guard-approved unattended work. Explicit user approval is
a separate human decision, not a `wiki-write-guard` approval.

### Class 5: Dangerous Writes

Examples:

- delete or rebuild canonical folders
- restore over live content
- mass rename or broad reorganization
- new root schema
- cross-agent truth merging
- automatic conflict resolution
- raw private logs or secrets into Markdown
- setup/config changes that alter agent discovery globally

Do not approve unattended. Return `escalate` or `reject`.

## Standard Obsidian Wiki Targets

For a normal standalone `obsidian-wiki` vault, the live content categories are:

```text
concepts/
entities/
skills/
references/
synthesis/
journal/
projects/
```

Support paths are:

```text
_raw/
_staging/
_archives/
_meta/
wiki-export/
```

Approved unattended targets in a standalone vault:

- Class 1: `wiki-export/`, `_staging/reports/`, `_insights.md`, generated `_meta/*.base`
- Class 2: `_raw/`, `_staging/`
- Class 3: existing files only, only if the maintenance checks pass

Live content category writes that add or change semantic claims are Class 4.
Only strictly mechanical Class 3 edits to existing files may be approved
unattended.

## Codex Memory Vault Boundary

If `vault_path` is `/home/alex/codex-memory-vault`, use the Codex memory-vault
schema. Generic standalone `obsidian-wiki` paths must be translated before
approval.

Canonical Codex paths:

```text
wiki/
entities/
decisions/
projects/
runbooks/
```

Non-canonical/support paths:

```text
staging/
reviews/
raw/
inbox/
.memvault/
```

Do not approve creation of these generic root directories in the Codex memory
vault:

```text
concepts/
skills/
references/
synthesis/
journal/
_staging/
_generated/
rules/
sources/
```

Translate generic targets:

| Generic target | Codex-vault target |
|---|---|
| `concepts/` | `wiki/` |
| `skills/` | `runbooks/` or project-specific how-to |
| `references/` | reviewed source summary in an approved canonical/support path |
| `synthesis/` | reviewed cross-domain analysis in approved path |
| `journal/` | normally not used; chat truth stays in raw logs and Graphiti |

Approved unattended targets in the Codex vault:

- Class 1: `reviews/`, `.memvault/reports/`
- Class 2: `staging/`, `inbox/`, `.memvault/queue/`
- Class 3: existing files only, only if the maintenance checks pass

Manifest, index, log, and hot-cache updates are writes. They may be approved
unattended only when they describe an approved Class 1, Class 2, or eligible
Class 3 operation and do not create canonical truth.

## Agent Boundaries

Always preserve `source_agent`.

- `codex`: may create Codex candidates or reports
- `claude`: may create sourced candidates or reports
- `copilot`: may create sourced candidates or reports
- `openclaw`: may create sourced candidates or reports
- `pi`: may create sourced candidates or reports
- `hermes`: external observed system; may create external-input candidates or
  reports only unless the user explicitly approved a bounded bridge

Hermes content must not become Codex canonical truth by default. Cross-agent
merging, especially Hermes into Codex memory, is Class 4 or Class 5 and must
escalate.

## Git Safety

This guard approves file writes only. It does not approve git commits, pushes,
branch changes, releases, package publishing, or global agent installation.

If a writer wants to commit or push, return `escalate`.

If the target vault is a git checkout on `main`, unattended writes are limited
to approved support paths for Class 1 and Class 2, or eligible Class 3
mechanical maintenance. Canonical truth changes on `main` must escalate.

## Review Queue

When decision is `queue`, the original target write is not allowed. The writer
may create a review-queue item in an approved support path.

For a standalone vault, use:

```text
_staging/review-queue/
```

For the Codex vault, use:

```text
reviews/review-queue/
```

The queue item must include:

- reason queued
- source agent
- source refs
- proposed target
- blocked write type
- safe next action
- whether the human operator, LI/reviewer, or only a later automated checker is
  needed

## Smoke Scenarios

Use these examples to check guard behavior:

| Scenario | Expected decision |
|---|---|
| Write a generated orphan report to `_staging/reports/orphan-report.md` | `approve` |
| Write a quick capture to `_raw/2026-06-27-finding.md` | `approve` |
| Write a staged candidate with full metadata to `_staging/concepts/foo.md` | `approve` |
| Append manifest/index/log entries for an approved staged candidate | `approve` |
| Add one unambiguous wikilink to one existing page, no semantic rewrite | `approve` |
| Write a new page to `concepts/foo.md` inside the Codex memory vault | `queue` or `reject` until translated |
| Promote a staging candidate into live canonical truth | `escalate` |
| Merge Hermes memory directly into Codex canonical truth | `escalate` |
| Delete, rebuild, restore, mass move, or create a new root schema | `escalate` or `reject` |
| Commit, push, publish, or install globally | `escalate` |

Machine smoke command:

```bash
python -m obsidian_wiki guard-dry-run --format json --fail-on-non-approve
```

This built-in all-scenario smoke intentionally exits non-zero because some
scenarios are supposed to `queue` or `escalate`. For a positive automation path
smoke, run:

```bash
python -m obsidian_wiki guard-dry-run \
  --scenario safe-log \
  --format json \
  --fail-on-non-approve
```

## Output Format

Return this compact result:

```text
Wiki Write Guard Result
- Decision: approve|queue|reject|escalate
- Operation class:
- Source agent:
- Target paths:
- Automatic: yes|no
- Reason:
- Required action:
```

For `approve`, the required action is "writer may apply the proposed write".

For `queue`, the required action is "write only the review-queue item; do not
write the original target".

For `reject` or `escalate`, the required action is "do not write target files".
