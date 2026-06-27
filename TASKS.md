# Obsidian Wiki Governance Tasklist

Status: draft
Created: 2026-06-26
Basis: `Korrigierte Grundentscheidung.pdf`

## Goal

Make `obsidian-wiki` useful as wiki/skill tooling without turning
`codex-memory-vault` into a chaotic, unreviewed memory dump.

## Corrected Core Decision

`OBSIDIAN_VAULT_PATH=/home/alex/codex-memory-vault` is allowed.

The risk is not the vault path itself. The risk is which operation writes what,
where, with which evidence and review level.

Therefore:

- read access to `codex-memory-vault` is allowed
- generated reports are allowed automatically if they are marked as generated
  and rebuildable
- staging/candidate writes are allowed automatically in approved staging
  locations
- small maintenance writes may run automatically after a short deterministic
  agent check
- canonical knowledge writes require Alex approval
- semantic policy/rule/decision changes require LI review before Alex decides
- destructive, root-schema, cross-scope, and mass rewrite operations are blocked
  unless explicitly approved with rollback/backup

## Automation Target

The goal is unattended memory upkeep, not manual review of every useful write.
Alex does not have the time to approve routine memory hygiene.

Allowed automatic writes:

- generated reports and inventories
- staging/candidate memory cards
- source coverage and review queue updates
- safe manifest/index bookkeeping for non-canonical generated or staging output
- small mechanical maintenance after deterministic checks

Not automatic by default:

- promotion into canonical truth
- semantic rule or architecture decisions
- cross-agent merging, especially Hermes into Codex memory
- deletion, broad moves, root-schema changes, or mass rewrites

Practical target: agents write useful candidate knowledge continuously, but the
system keeps final truth, risky boundaries, and destructive actions guarded.

## Automated Review Loop

Routine memory writes should not depend on Alex being present.

Use a two-step automated path:

1. A writer step prepares the intended change as a small, inspectable plan or
   diff.
2. A checker step validates the write class, target path, metadata, scope,
   source references, and boundary rules before the write is accepted.

If the checker approves a Class 1, Class 2, or eligible Class 3 write, the write
may continue unattended.

If the checker rejects or cannot classify the write, the system must not ask
Alex immediately for routine work. It should write a review-queue item instead,
with the reason, source, proposed target, and safe next action.

Only Class 4 and Class 5 work should require Alex or LI escalation by default.
For semantic policy, architecture, agent-boundary, retention, or security
changes, the LI can act as the automated expert reviewer before Alex decides.

## Existing System Roles

- `codex-memory-vault`: human-readable canonical/staging Markdown memory surface
- `codex_gedaechtnis`: runtime memory with raw logs and Graphiti/FalkorDB
- Graphiti/FalkorDB: episodic and temporal working memory, not canonical truth
- Kiro/Redis: retrieval/index/cache layer, not canonical truth
- `obsidian-wiki`: skill/tooling system for wiki maintenance, not an autonomous
  truth engine
- Obsidian: human-facing Markdown/wiki interface

## Hard Boundaries

- Do not treat raw chat, LLM summaries, Graphiti facts, Redis hits, or generated
  reports as canonical truth.
- Do not create new root schemas in `codex-memory-vault` until checked against
  the vault's own `AGENTS.md` and runbooks.
- Do not blindly adopt directory names from external recommendations such as
  `_staging`, `_generated`, `rules`, `concepts`, or `sources`.
- Do not run `setup.sh` until its write behavior is made predictable.
- Do not commit private raw logs, secrets, tokens, local scratch logs, or
  unreviewed dumps.
- Do not mix Codex, Hermes, Claude, OpenClaw, or shared/global scope by default.

## Write Classes

### Class 0: Read-Only

Examples:

- read Markdown
- search vault
- inspect frontmatter
- list backlinks
- list recent changes

Default: allowed.

Done when:

- read-only tools do not mutate files, indexes, or runtime state

### Class 1: Generated Reports

Examples:

- link report
- orphan report
- status dashboard
- source coverage
- review queue summary

Default: allowed only in approved generated/report locations.

Done when:

- reports are clearly rebuildable
- generated reports are excluded from canonical truth by default
- generated output does not overwrite human-authored canonical pages

### Class 2: Staging Candidate Writes

Examples:

- candidate memory card
- decision draft
- rule draft
- conflict card
- paper/source card

Default: allowed only in approved staging/candidate locations.

Required metadata:

- `id`
- `status`
- `type`
- `title`
- `scope`
- `created_at`
- `updated_at`
- `confidence`
- `review_state`
- `owners`
- `source_refs` or explicit reason why source is missing

Done when:

- candidates cannot be mistaken for canonical truth
- candidates carry scope and source context

### Class 3: Small Maintenance Writes

Examples:

- unambiguous link fix
- alias addition
- mechanical frontmatter normalization
- update of a clearly marked generated block

Default: allowed only after short deterministic agent check.

Checks:

- target path allowed
- small diff: max 3 files and max 80 changed lines unless Alex approves more
- no delete
- no rename
- no mass rename
- no root schema change
- no scope escalation
- no cross-agent mixup
- `git diff --stat` reviewed
- `git diff --check` passes
- git diff available

Done when:

- maintenance writes are small, reviewable, and reversible

### Class 4: Canonical Knowledge Writes

Examples:

- new durable rule
- new architecture decision
- change to existing canonical knowledge page
- staging-to-canonical promotion
- deprecation of old rule
- conflict resolution

Default: Alex approval required.

LI review required when:

- the change affects rules, policies, decisions, security, retention, agent
  boundaries, or shared/global scope

Done when:

- source references exist
- conflict check has been done
- Alex approval is explicit
- LI review exists for semantic/system-level changes
- git diff is visible before commit

### Class 5: Dangerous Writes

Examples:

- delete or rebuild canonical folders
- mass rename
- broad reorganization
- new top-level schemas
- cross-scope/global promotion
- automatic conflict resolution
- secrets/raw logs into Markdown

Default: blocked.

Allowed only with:

- Alex approval
- LI check
- backup/rollback path
- explicit manual command

Done when:

- destructive or broad operations cannot happen as accidental agent behavior

## Tasks

### 1. Current State Inventory

Mode: read-only.

Check:

- `OBSIDIAN_VAULT_PATH`
- `OBSIDIAN_WIKI_REPO`
- global skill links under `~/.codex`, `~/.claude`, `~/.hermes`,
  `~/.openclaw`, `~/.agents`, `~/.gemini`
- local repo symlinks under `.agents`, `.claude`, `.cursor`, `.windsurf`
- untracked files including `log.md`
- whether `.skills/*-history-ingest` implementations are tracked

Done when:

- every changed/untracked path is classified as keep, regenerate, ignore,
  remove, or needs Alex decision

### 2. Decide `log.md`

Mode: classify before write.

Original fact:

- `log.md` was an untracked local file in `obsidian-wiki`.
- It contained project/query log content and must not be committed blindly.
- `AGENTS.md` and `SETUP.md` describe `log.md` as a normal repository activity
  log, so the filename itself must not be blocked globally.

Decision:

- Do not add `log.md` itself to `.gitignore`.
- Add a local ignored quarantine folder: `.local-quarantine/`.
- Move unclear or misplaced files there until their real target is known.
- Later, a classifier/check agent may inspect quarantine contents and recommend
  delete, restore, or move-to-project-vault actions.

Outcome:

- 2026-06-26: moved the misplaced ArchaeoTerrain/Planlauf query log to
  `.local-quarantine/2026-06-26_obsidian-wiki_log_archaeoterrain_misplaced.md`.
- `.local-quarantine/` is ignored by Git; `log.md` itself remains an allowed
  repository activity-log filename.

Done when:

- `log.md` is no longer an unexplained untracked file
- no private raw logs or project scratch notes are committed accidentally

Status: done for the current misplaced file.

### 3. Align With Vault Governance

Mode: read-only first, then documentation change if needed.

Check the actual `codex-memory-vault` governance before defining staging or
generated paths.

Do not assume `_staging`, `_generated`, `rules`, `concepts`, or `sources` are
allowed just because the external recommendation used those names.

Expected known starting point to verify:

- canonical candidates likely map to `wiki/`, `entities/`, `decisions/`,
  `projects/`, and `runbooks/`
- non-canonical/support areas may include `staging/`, `reviews/`, `raw/`,
  `inbox/`, and `.memvault/`

Done when:

- allowed canonical, staging, and generated locations are known
- external naming is translated into the existing vault schema
- an explicit allowlist exists for canonical paths
- an explicit allowlist exists for non-canonical/report/staging paths
- no new root directory is introduced without vault-governance approval

Outcome:

- 2026-06-26: read-only checked `codex-memory-vault` governance:
  `AGENTS.md`, `runbooks/00_START_HERE.md`,
  `runbooks/01_VAULT_OPERATING_RULES.md`, and
  `runbooks/reference/OBSIDIAN_WIKI_COMPATIBILITY.md`.
- Canonical allowlist for reviewed memory:
  `wiki/`, `entities/`, `decisions/`, `projects/`, `runbooks/`.
- Non-canonical/support allowlist:
  `staging/`, `reviews/`, `raw/`, `inbox/`, `.memvault/`.
- `obsidian-wiki` schema terms must be translated instead of copied:
  `concepts/` -> `wiki/`; `skills/` -> `runbooks/` or project how-tos;
  `journal/` is not used by default because chat truth stays in raw logs and
  Graphiti.
- No new root schemas such as `concepts/`, `skills/`, `references/`,
  `synthesis/`, or `journal/` may be created in `codex-memory-vault` without
  explicit Alex approval.

Status: done read-only.

### 4. Add Boundary Rule To `obsidian-wiki`

Mode: documentation change after task 3.

Define in `AGENTS.md`:

- `obsidian-wiki` is tooling, not canonical truth
- `codex-memory-vault` may be the vault path
- write class determines permissions
- canonical writes require Alex approval
- LI review is required for semantic/system-level memory changes
- generic root schemas are not allowed

Done when:

- an agent can read the rule before using wiki skills
- the rule explicitly translates the external `obsidian-wiki` schema into the
  current `codex-memory-vault` schema instead of copying it

Outcome:

- 2026-06-26: added `Codex Memory Vault Boundary` to `AGENTS.md`.
- The rule states that `obsidian-wiki` is tooling, not canonical truth.
- It allows `codex-memory-vault` as `OBSIDIAN_VAULT_PATH` but requires the
  existing Codex vault schema: `wiki/`, `entities/`, `decisions/`, `projects/`,
  `runbooks/`.
- It blocks unmanaged root schemas such as `concepts/`, `skills/`,
  `references/`, `synthesis/`, and `journal/` inside the Codex memory vault
  unless Alex explicitly approves a schema migration.
- It records that unclear files go to `.local-quarantine/` first and that
  ArchaeoTerrain/Planlauf content belongs to its own project/vault.
- LI recheck requested two clarifications before commit:
  the Codex Memory Vault boundary overrides generic standalone skill
  instructions, and quarantine means the repo-local
  `/home/alex/obsidian-wiki/.local-quarantine/`, not a new vault root.

Status: implemented and LI recommendation applied.

### 5. Make `setup.sh` Safe

Mode: script change after task 1.

Change `setup.sh` so that:

- default mode is dry-run or local-only
- global skill installation is opt-in
- planned create/remove/link actions are printed before writes
- real directories are never overwritten
- non-owned symlinks are not overwritten without explicit approval
- repo-internal links are relative or consistently generated

Done when:

- running setup cannot silently widen Codex/Hermes/OpenClaw/Claude access
- running setup cannot recreate absolute repo-internal links
- global skill symlink writes require explicit opt-in
- no global skill symlink is created or replaced without preview

Outcome:

- 2026-06-26: `setup.sh` now separates repo-local skill links from global skill
  links.
- Repo-local skill links are generated as relative links to
  `../../.skills/<skill>`, avoiding committed `/Users/...` or `/home/alex/...`
  targets.
- Global skill symlink writes are now opt-in via `bash setup.sh --global-skills`.
- `bash setup.sh --dry-run` previews planned writes without changing files.
- The default run is local-only: it uses `.env`, updates repo-local discovery
  links, and skips `~/.obsidian-wiki/config` plus global skill symlinks.
- `bash setup.sh --global-skills` implies global config and global skill
  symlinks, and each create/remove/link/write action is printed before it runs.
- Existing real files/directories are skipped; non-owned symlinks are skipped
  unless `--force` is explicitly used after review.
- LI recheck found three blockers: unconditional `~/.obsidian-wiki` directory
  creation, unchecked global config overwrite, and too-broad owned-link matching
  for global symlinks.
- 2026-06-27: fixed those blockers. Default and dry-run no longer create
  `~/.obsidian-wiki`; existing global config is checked and not overwritten;
  repo legacy link matching is allowed only for repo-local links; global links
  require exact ownership or explicit `--force`.
- Setup summary now distinguishes local repo links from optional global links.

Status: implemented; final LI recheck passed on 2026-06-27.

### 6. Normalize Skill Discovery Links

Mode: filesystem change after task 5.

Target policy:

- no tracked symlink points to `/Users/...`
- no tracked symlink points to `/home/alex/obsidian-wiki/...`
- repo-internal discovery links are relative or intentionally generated
- untracked history-ingest discovery links are either added intentionally or
  generated/ignored intentionally

Done when:

- no broken symlinks
- diff contains only intentional link policy changes
- no global symlink write is performed by this task

Outcome:

- 2026-06-26: regenerated only repo-local discovery links under `.agents`,
  `.claude`, `.cursor`, and `.windsurf`.
- All repo-local discovery links now point to relative targets such as
  `../../.skills/wiki-query`.
- No global skill symlink write was performed.
- 2026-06-27: checked Task 6 done criteria:
  no broken repo-local symlinks, no repo-local symlink target points to
  `/Users/...` or `/home/alex/obsidian-wiki/...`, and every `.skills/*`
  implementation has corresponding repo-local discovery links.
- The new history-ingest discovery links for `codex-history-ingest`,
  `hermes-history-ingest`, `openclaw-history-ingest`, and `wiki-history-ingest`
  are intentional because the matching `.skills/<name>` directories exist.

Status: implemented.

### 7. Audit History-Ingest Skills

Mode: read-only first.

Check each history-ingest skill for:

- source histories it reads
- write target
- dry-run/inventory behavior
- staging behavior
- canonical promotion behavior
- Codex/Hermes/Claude/OpenClaw boundary handling

Done when:

- each skill is classified as safe as-is, needs guardrail, or blocked until
  Alex decides

Outcome:

- 2026-06-27: read-only audited the five history-ingest skills:
  `claude-history-ingest`, `codex-history-ingest`,
  `hermes-history-ingest`, `openclaw-history-ingest`, and
  `wiki-history-ingest`.
- `claude-history-ingest`: needs guardrail. It reads `~/.claude` project
  memories and conversation JSONL, then writes generic wiki pages plus
  `.manifest.json`, `index.md`, and `log.md`.
- `codex-history-ingest`: needs guardrail. It reads `~/.codex` session index,
  rollout JSONL, and optional history files. It is especially sensitive because
  Codex logs can contain system/developer prompts, tool payloads, secrets, and
  operational telemetry.
- `hermes-history-ingest`: blocked for Codex-vault write mode until Alex
  explicitly approves a bounded bridge. It reads `~/.hermes` memories/sessions,
  but Hermes is a separate external agent system and must not become Codex
  canonical truth by default.
- `openclaw-history-ingest`: needs guardrail. It reads `~/.openclaw`
  `MEMORY.md`, daily notes, dreams, and sessions. It already skips credentials
  in the written instruction, but its write targets and promotion path are still
  too generic for the Codex memory vault.
- `wiki-history-ingest`: needs guardrail. It is only a router, but currently
  tells the agent to execute destination skills exactly, so it must pass through
  the same write-mode and boundary checks.
- Main issue: the four write-capable skills use the generic standalone wiki
  schema (`concepts/`, `skills/`, `synthesis/`, `index.md`, `log.md`,
  `.manifest.json`). For `OBSIDIAN_VAULT_PATH=/home/alex/codex-memory-vault`,
  writes must instead respect the Codex-vault boundary from `AGENTS.md`.
- Required guardrails for Task 8:
  inventory/dry-run as default; explicit Alex approval for writes; staging-first
  candidate output; `source_agent` metadata; no canonical promotion without
  approval; Hermes marked as external input; manifest/index/log writes treated
  as writes; router must forward the selected mode and guard result.
- LI recheck agreed that Task 7 should only document and classify. Skill-code
  changes belong in Task 8.

Status: audited; guardrails required before any history-ingest write mode.

### 8. Add Minimal Write Guard

Mode: code/tooling change only after tasks 3, 4, and 7.

Create or adapt a small guard that enables unattended safe writes and blocks or
escalates risky writes.

The guard should support an automated writer/checker flow: a write-capable skill
first prepares a proposed operation, then the checker approves, rejects, or
routes it to a review queue. Alex should not be required for routine Class 1,
Class 2, or eligible Class 3 writes.

The guard must check:

- operation class
- target path
- diff size
- source reference
- scope
- dangerous path patterns
- whether Alex/LI approval is required
- checker result: approve, reject, or queue-for-review

Done when:

- generic wiki writes cannot bypass the write class policy
- no write-capable skill can write directly without a checker result
- generated/report writes can run without Alex when they target approved
  generated/report locations
- staging/candidate writes can run without Alex when they carry required
  metadata and target approved staging locations
- small mechanical maintenance can run without Alex after deterministic checks
- rejected or unclear routine writes create review-queue items instead of
  blocking Alex in the moment
- every write-capable skill is either routed through the guard or explicitly
  remains read-only/blocked
- canonical promotion, semantic policy changes, cross-agent truth merging,
  deletion, broad moves, root-schema changes, and mass rewrites require
  escalation instead of silent execution
- smoke tests can exercise allow/block decisions

Outcome:

- 2026-06-27: added `.skills/wiki-write-guard/SKILL.md` as the shared
  writer/checker guard.
- The guard classifies proposed writes as `approve`, `queue`, `reject`, or
  `escalate`.
- The guard allows unattended Class 1 generated reports, Class 2 staging
  candidates, and eligible Class 3 mechanical maintenance when target paths,
  metadata, source references, scope, and boundary rules pass.
- The guard routes unclear routine writes to `reviews/review-queue/` instead of
  blocking Alex in the moment.
- The guard escalates canonical promotion, semantic policy changes, cross-agent
  truth merging, deletion, broad moves, root-schema changes, rebuilds, and
  restores.
- Added `wiki-write-guard` to `AGENTS.md` routing and README skill list.
- Added Write Guard sections to write-capable skills:
  `wiki-ingest`, `data-ingest`, `wiki-update`, `cross-linker`,
  `tag-taxonomy`, `wiki-lint`, `wiki-query`, `wiki-export`, `wiki-status`,
  `wiki-setup`, `wiki-rebuild`, `claude-history-ingest`,
  `codex-history-ingest`, `hermes-history-ingest`,
  `openclaw-history-ingest`, and `wiki-history-ingest`.
- Regenerated repo-local skill discovery links only. No global skill symlinks
  were written.

Status: implemented; Task 9 smoke tests are next.

### 9. Smoke Tests

Mode: read-only or temp-test writes only where explicitly safe.

Required tests:

- vault path can be read
- generated report write allowed only in generated/report location
- staging candidate write allowed only in staging/candidate location
- canonical rule write blocked without Alex approval
- source-less canonical promotion blocked
- cross-scope escalation blocked or requires Alex + LI
- destructive rebuild blocked
- generated/staging content excluded from canonical truth by default
- no canonical write, commit, or push directly to `main` without approval
- no global skill symlink write without explicit opt-in

Done when:

- tests prove the write policy works before real wiki writes are enabled

Outcome:

- 2026-06-27: ran static smoke checks for the write-guard path.
- `OBSIDIAN_VAULT_PATH` resolves to `/home/alex/codex-memory-vault`.
- Vault directory exists and is readable.
- The vault is currently on git branch `langgraph-agent-system`, not `main`.
- `wiki-write-guard` contains smoke scenarios for:
  approved generated report writes, approved staging candidate writes, approved
  manifest/index/log bookkeeping for approved staging output, approved small
  mechanical link maintenance, rejected/queued generic `concepts/` writes in
  the Codex vault, escalated canonical promotion, escalated Hermes-to-Codex
  truth merge, and escalated destructive/broad writes.
- Repo-local discovery links for `wiki-write-guard` exist and resolve under:
  `.agents/skills/`, `.claude/skills/`, `.cursor/skills/`, and
  `.windsurf/skills/`.
- `setup.sh --dry-run` reports no global skill symlink write and no global
  `~/.obsidian-wiki/config` write.
- All write-capable skills checked in Task 8 contain a `Write Guard` section.
- Static decision trace:

  | Case | Expected guard decision | Evidence |
  |---|---|---|
  | Generated orphan report to `reviews/orphan-report.md` | approve | Class 1 allows rebuildable reports in approved report/support locations. |
  | Staging candidate with full metadata to `staging/candidate-123.md` | approve | Class 2 allows candidate writes with required metadata and explicit `source_agent`. |
  | Manifest/index/log bookkeeping for approved staging output | approve | Manifest/index/log updates are allowed only when attached to an approved Class 1/2/3 operation. |
  | One unambiguous wikilink in one existing page | approve | Class 3 allows small mechanical maintenance with no semantic rewrite, delete, move, or boundary change. |
  | New page at `concepts/foo.md` in Codex memory vault | queue/reject | Codex vault blocks unmanaged generic root schemas until translated by the guard. |
  | Promote staging candidate into `wiki/` as durable truth | escalate | Canonical knowledge writes are Class 4 and not unattended. |
  | Merge Hermes memory directly into Codex canonical truth | escalate | Hermes is an external observed system; cross-agent truth merging escalates. |
  | Delete/rebuild/restore/mass move/new root schema | escalate/reject | Class 5 dangerous writes are not unattended. |
  | Commit or push after a file write | escalate | `wiki-write-guard` approves file writes only, never git commit/push. |

Status: smoke checked statically; no real vault writes were performed.

### 10. Commit Plan

Mode: commit only after Alex approval.

Preferred split:

1. governance tasklist
2. `log.md` policy
3. boundary documentation
4. setup safety
5. symlink normalization
6. history-ingest guardrails

Done when:

- no broad dirty-state commit is made
- each commit has one clear purpose
