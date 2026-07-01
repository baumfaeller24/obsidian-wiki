---
name: wiki-tools
description: Route less-common obsidian-wiki tasks to the right bundled skill without loading every skill globally. Use this in Codex minimal-profile setups when the user asks for wiki export/import, rebuild, dedup, synthesis, dashboards, digests, research, graph coloring, tag cleanup, cross-linking, memory bridge, history ingest variants, vault switching, skill factory, or any obsidian-wiki command/tool that is not already available as a first-class global skill.
---

# Wiki Tools Router

This is a lightweight router for agents that intentionally keep only a small
global obsidian-wiki skill profile. Do not implement the target workflow here.
Find the matching bundled skill, read its `SKILL.md` completely, and then follow
that skill's instructions.

## Resolve the Skill Root

Find the obsidian-wiki repository or packaged data root:

1. Read `OBSIDIAN_WIKI_REPO` from the nearest `.env` walking up from the current
   directory.
2. If not found, read `~/.obsidian-wiki/config`.
3. If still not found and the `obsidian-wiki` CLI is available, run
   `obsidian-wiki info` or `python -m obsidian_wiki info` and use the reported
   `skills:` directory.
4. The target skill root is usually `$OBSIDIAN_WIKI_REPO/.skills`. If
   `OBSIDIAN_WIKI_REPO` already points at a package data directory, use its
   `skills/` child if present.

If the target skill file cannot be found, stop and tell the user which skill is
missing and which paths were checked.

## Routing Table

Use this table to choose exactly one target skill. Then read:

```text
<skill-root>/<target-skill>/SKILL.md
```

| User intent | Target skill |
|---|---|
| Generic document, URL, raw text, transcript, ChatGPT export, or PDF ingest | `wiki-ingest` |
| Old `/data-ingest`, `/ingest-url`, or `/obsidian-wiki-ingest` wording | `wiki-ingest` |
| Bulk Claude/Codex/Copilot/Hermes/OpenClaw/Pi history ingest | `wiki-history-ingest` |
| Topic-first search in one agent's raw history, `/wiki-codex`, `/wiki-claude`, etc. | `wiki-agent` |
| Cross-link pages or add missing wikilinks | `cross-linker` |
| Normalize or audit tags | `tag-taxonomy` |
| Color-code the Obsidian graph | `graph-colorize` |
| Create dashboards, Bases, or Dataview-style views | `wiki-dashboard` |
| Weekly/daily/monthly knowledge digest | `wiki-digest` |
| Find or merge duplicate concept pages | `wiki-dedup` |
| Create cross-topic synthesis pages | `wiki-synthesize` |
| Compare what different agents know | `memory-bridge` |
| Autonomous web research filed into the wiki | `wiki-research` |
| Export graph, OKF bundle, GraphML, Cypher, or HTML views | `wiki-export` |
| Import graph stubs or OKF markdown bundles | `wiki-import` |
| Switch vault profiles | `wiki-switch` |
| Archive, rebuild, or restore a vault | `wiki-rebuild` |
| Turn mature wiki pages into a portable Agent Skill | `vault-skill-factory` |
| Explain the LLM wiki architecture or page schema | `llm-wiki` |
| Create or improve a skill | `skill-creator` |

If multiple rows match, prefer the narrowest target skill. For example, a
request to import Codex history should route to `wiki-history-ingest`, not
generic `wiki-ingest`.

## Execution Rules

1. Read the chosen target skill's `SKILL.md` completely before acting.
2. If that skill references a required relative file, resolve it relative to the
   target skill directory and read only the needed reference.
3. Respect the target skill's `wiki-write-guard`, config resolution, and
   verification steps.
4. For high-risk operations such as rebuild, restore, import, broad dedup,
   global setup, deleting files, commit, push, or publishing, require explicit
   current user approval before making changes.
5. Report clearly when only routing/static checks were performed and when a
   runtime path was actually verified.

## Fallback

If the user's intent is unclear, ask one short clarifying question naming the
two most likely target skills. If no target skill fits, continue with normal
repo inspection and explain that no bundled wiki skill matched the request.
