# Obsidian Wiki — Agent Context

A **skill-based framework** for building and maintaining an Obsidian knowledge base. No scripts or dependencies — everything is markdown instructions that you execute directly.

## Configuration

Read config in this order (first found wins):

1. **`~/.obsidian-wiki/config`** — global config, works from any project directory
2. **`.env`** in the obsidian-wiki repo — local fallback

Both files set `OBSIDIAN_VAULT_PATH` (where the wiki lives). The global config also sets `OBSIDIAN_WIKI_REPO` (where this repo is cloned).

## Codex Memory Vault Boundary

`obsidian-wiki` is a tooling layer. It can query, lint, cross-link, export, and
help maintain markdown pages. It is not the canonical memory authority.

If `OBSIDIAN_VAULT_PATH` points to Alex's Codex memory vault, use the existing
Codex vault schema instead of creating the generic `obsidian-wiki` schema.
This boundary overrides generic skill instructions that would otherwise create
standalone `obsidian-wiki` folders in the Codex memory vault.

Canonical Codex memory may live only in:

```text
wiki/
entities/
decisions/
projects/
runbooks/
```

Non-canonical working areas are:

```text
staging/
reviews/
raw/
inbox/
.memvault/
```

Translate generic `obsidian-wiki` terms into the Codex vault schema:

| Generic term | Codex memory-vault target |
|---|---|
| `concepts/` | `wiki/` |
| `skills/` | `runbooks/` or project-specific how-tos |
| `references/` | reviewed source summaries, not raw dumps |
| `synthesis/` | reviewed cross-domain analysis in an approved canonical directory |
| `journal/` | not used by default; chat truth stays in raw logs and Graphiti |

Do not create root directories such as `concepts/`, `skills/`,
`references/`, `synthesis/`, or `journal/` inside the Codex memory vault unless
Alex explicitly approves a schema migration.

Canonical writes require Alex approval. Semantic, policy, system-boundary,
agent-boundary, retention, or security changes require LI review before commit.

## Automated Write Guard

Routine wiki maintenance should run without Alex being present, but no
write-capable skill may write directly to a vault without first applying the
`wiki-write-guard` checker.

Required flow:

1. Writer prepares a proposed operation.
2. `wiki-write-guard` classifies it as approve, queue, reject, or escalate.
3. Writer proceeds only on approve.

Generated reports, staging candidates, and eligible small mechanical
maintenance may be approved unattended. Unclear routine work should become a
review-queue item instead of interrupting Alex. Canonical promotion, semantic
policy/architecture changes, cross-agent truth merging, deletion, broad moves,
root-schema changes, rebuilds, and restores must escalate.

Unclear or misplaced files go to this tooling repo's local quarantine folder
`/home/alex/obsidian-wiki/.local-quarantine/` first. Do not delete or commit
them until their correct project/vault is known. ArchaeoTerrain/Planlauf content
belongs to its own project/vault, not to the Codex memory vault or this tooling
repo.

## Generic Vault Structure

Use this structure only for a normal standalone `obsidian-wiki` vault. Do not
copy it into the Codex memory vault.

```
$OBSIDIAN_VAULT_PATH/
├── index.md                # Master index — every page listed, always kept current
├── log.md                  # Chronological activity log (ingests, updates, lints)
├── .manifest.json          # Tracks every ingested source: path, timestamps, pages produced
├── _meta/
│   └── taxonomy.md         # Controlled tag vocabulary
├── _insights.md            # Graph analysis output (hubs, bridges, dead ends)
├── _raw/                   # Staging area — drop rough notes here, next ingest promotes them
├── concepts/               # Abstract ideas, patterns, mental models
├── entities/               # Concrete things — people, tools, libraries, companies
├── skills/                 # How-to knowledge, techniques, procedures
├── references/             # Factual lookups — specs, APIs, configs
├── synthesis/              # Cross-cutting analysis connecting multiple concepts
├── journal/                # Time-bound entries — daily logs, session notes
└── projects/
    └── <project-name>.md   # One page per project synced via wiki-update
```

Every wiki page has required frontmatter: `title`, `category`, `tags`, `sources`, `created`, `updated`. Pages connect via `[[wikilinks]]`.

## Skill Routing

Skills live in `.skills/<name>/SKILL.md`. Match the user's intent to the right skill:

| User says something like… | Skill |
|---|---|
| "set up my wiki" / "initialize" | `wiki-setup` |
| "check this wiki write" / "guard wiki write" / any write-capable skill before writing | `wiki-write-guard` |
| "/wiki-history-ingest claude" / "/wiki-history-ingest codex" / "/wiki-history-ingest hermes" | `wiki-history-ingest` |
| "ingest" / "add this to the wiki" / "process these docs" | `wiki-ingest` |
| "import my Claude history" / "mine my conversations" | `claude-history-ingest` |
| "import my Codex history" / "mine my Codex sessions" | `codex-history-ingest` |
| "import my Hermes history" / "mine my Hermes memories" / "ingest ~/.hermes" | `hermes-history-ingest` |
| "import my OpenClaw history" / "mine my OpenClaw sessions" / "ingest ~/.openclaw" | `openclaw-history-ingest` |
| "process this export" / "ingest this data" / logs, transcripts | `data-ingest` |
| "what's the status" / "what's been ingested" / "show the delta" | `wiki-status` |
| "wiki insights" / "hubs" / "wiki structure" | `wiki-status` (insights mode) |
| "what do I know about X" / "find info on Y" / any question | `wiki-query` |
| "audit" / "lint" / "find broken links" / "wiki health" | `wiki-lint` |
| "rebuild" / "start over" / "archive" / "restore" | `wiki-rebuild` |
| "link my pages" / "cross-reference" / "connect my wiki" | `cross-linker` |
| "fix my tags" / "normalize tags" / "tag audit" | `tag-taxonomy` |
| "update wiki" / "sync to wiki" / "save this to my wiki" | `wiki-update` |
| "export wiki" / "export graph" / "graphml" / "neo4j" | `wiki-export` |
| "create a new skill" | `skill-creator` |

## Cross-Project Usage

The main use case: you're working in some other project and want to sync knowledge into your wiki or query it. Two global skills handle this — `wiki-update` and `wiki-query`. They work from any directory.

### wiki-update (write to wiki)

1. Read `~/.obsidian-wiki/config` to get `OBSIDIAN_VAULT_PATH`
2. Scan the current project: README, source structure, git log, package metadata
3. Distill what's worth remembering (architecture decisions, patterns, trade-offs — not code listings)
4. Write to `$VAULT/projects/<project-name>.md`, cross-linking to concept/entity pages as needed
5. Update `.manifest.json`, `index.md`, and `log.md`

On repeat runs, it checks `last_commit_synced` in `.manifest.json` and only processes the delta via `git log <last_commit>..HEAD`.

### wiki-query (read from wiki)

1. Read `~/.obsidian-wiki/config` to get `OBSIDIAN_VAULT_PATH`
2. Scan titles, tags, and `summary:` frontmatter fields first (cheap pass)
3. Only open page bodies when the index pass can't answer
4. Return a synthesized answer with `[[wikilink]]` citations

## Visibility Tags (optional)

Pages can carry a `visibility/` tag to mark their intended reach. **This is entirely optional** — untagged pages behave exactly as they always have (visible everywhere). The system stays single-vault, single source of truth.

| Tag | Meaning |
|---|---|
| *(no tag)* | Same as `visibility/public` — visible in all modes |
| `visibility/public` | Explicitly public — visible in all modes |
| `visibility/internal` | Team-only — excluded when querying in filtered mode |
| `visibility/pii` | Sensitive data — excluded when querying in filtered mode |

**Filtered mode** is opt-in, triggered by phrases like "public only", "user-facing answer", "no internal content", or "as a user would see it" in a query. Default mode shows everything.

`visibility/` tags are **system tags** — they don't count toward the 5-tag limit and are listed separately from domain/type tags in the taxonomy.

See `wiki-query` and `wiki-export` skills for how the filter is applied.

## Core Principles

- **Compile, don't retrieve.** The wiki is pre-compiled knowledge. Update existing pages — don't append or duplicate.
- **Track everything.** Update `.manifest.json` after ingesting, `index.md` and `log.md` after any operation.
- **Connect with `[[wikilinks]]`.** Every page should link to related pages. This is what makes it a knowledge graph, not a folder of files.
- **Frontmatter is required.** Every wiki page needs: `title`, `category`, `tags`, `sources`, `created`, `updated`.
- **Single source of truth.** Visibility tags shape how content is surfaced — they don't duplicate or separate it.

## Architecture Reference

For the full pattern (three-layer architecture, page templates, project org), read `.skills/llm-wiki/SKILL.md`.
