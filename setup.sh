#!/bin/bash
#
# obsidian-wiki setup — configures skill discovery for all supported AI agents.
#
# Usage:
#   bash setup.sh [--dry-run]
#   bash setup.sh --global-skills [--dry-run]
#
# What it does:
#   1. Creates .env from .env.example (if not present)
#   2. Symlinks .skills/* into each agent's expected skills directory:
#      - .claude/skills/    (Claude Code)
#      - .cursor/skills/    (Cursor)
#      - .windsurf/skills/  (Windsurf)
#      - .agents/skills/    (Antigravity / generic agents)
#   3. Optionally writes ~/.obsidian-wiki/config with --global-config
#   4. Optionally symlinks skills globally with --global-skills
#   5. Prints a summary of what's ready
#
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/.skills"
DRY_RUN=0
FORCE=0
INSTALL_GLOBAL_CONFIG=0
INSTALL_GLOBAL_SKILLS=0

for arg in "$@"; do
  case "$arg" in
    --dry-run)
      DRY_RUN=1
      ;;
    --force)
      FORCE=1
      ;;
    --global-config)
      INSTALL_GLOBAL_CONFIG=1
      ;;
    --global-skills|--install-global-skills)
      INSTALL_GLOBAL_SKILLS=1
      INSTALL_GLOBAL_CONFIG=1
      ;;
    -h|--help)
      echo "Usage: bash setup.sh [--dry-run] [--global-config] [--global-skills] [--force]"
      echo ""
      echo "Default: configure this repository only."
      echo "--dry-run: print planned writes without changing files."
      echo "--global-config: also write ~/.obsidian-wiki/config."
      echo "--global-skills: also install symlinks under ~/.claude, ~/.codex, ~/.hermes, ~/.openclaw, ~/.agents, and ~/.gemini; implies --global-config."
      echo "--force: replace non-owned symlinks. Use only after reviewing the dry-run."
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: bash setup.sh [--dry-run] [--global-config] [--global-skills] [--force]" >&2
      exit 2
      ;;
  esac
done

plan() {
  echo "PLAN: $*"
}

run_cmd() {
  plan "$*"
  if [ "$DRY_RUN" = "1" ]; then
    return 0
  fi
  "$@"
}

ensure_dir() {
  local target_dir="$1"
  if [ ! -d "$target_dir" ]; then
    run_cmd mkdir -p "$target_dir"
  fi
}

write_global_config() {
  ensure_dir "$GLOBAL_CONFIG_DIR"
  local desired_config
  desired_config=$(cat <<EOF
OBSIDIAN_VAULT_PATH="$VAULT_PATH"
OBSIDIAN_WIKI_REPO="$SCRIPT_DIR"
EOF
)
  if [ -f "$GLOBAL_CONFIG" ]; then
    if [ "$(cat "$GLOBAL_CONFIG")" = "$desired_config" ]; then
      echo "OK: $GLOBAL_CONFIG already matches desired config"
      return 0
    fi
    echo "SKIP: $GLOBAL_CONFIG already exists and differs"
    echo "      Edit it manually if you want to change global config."
    return 0
  elif [ -e "$GLOBAL_CONFIG" ]; then
    echo "SKIP: $GLOBAL_CONFIG exists and is not a regular file"
    return 0
  fi

  plan "write $GLOBAL_CONFIG"
  if [ "$DRY_RUN" = "1" ]; then
    return 0
  fi
  printf '%s\n' "$desired_config" > "$GLOBAL_CONFIG"
}

is_owned_skill_link() {
  local current_target="$1"
  local skill_name="$2"
  local expected_target="$3"
  local mode="$4"

  case "$current_target" in
    "$expected_target" | \
    "$expected_target/" | \
    "$SKILLS_DIR/$skill_name" | "$SKILLS_DIR/$skill_name/" | \
    "$SCRIPT_DIR/.skills/$skill_name" | "$SCRIPT_DIR/.skills/$skill_name/")
      return 0
      ;;
  esac

  if [ "$mode" = "repo" ]; then
    case "$current_target" in
      "../../.skills/$skill_name" | \
      */obsidian-wiki/.skills/"$skill_name" | */obsidian-wiki/.skills/"$skill_name"/)
        return 0
        ;;
    esac
  fi

  return 1
}

link_skill() {
  local target_dir="$1"
  local skill_name="$2"
  local target="$3"
  local mode="$4"
  local link_path="$target_dir/$skill_name"

  if [ -L "$link_path" ]; then
    local current_target
    current_target="$(readlink "$link_path")"
    if [ "$current_target" = "$target" ]; then
      echo "OK: $link_path -> $target"
      return 0
    fi
    if is_owned_skill_link "$current_target" "$skill_name" "$target" "$mode" || [ "$FORCE" = "1" ]; then
      echo "REPLACE: $link_path $current_target -> $target"
      run_cmd rm "$link_path"
    else
      echo "SKIP: $link_path points to non-owned target: $current_target"
      echo "      Review first, then rerun with --force if replacement is intended."
      return 0
    fi
  elif [ -e "$link_path" ]; then
    echo "SKIP: $link_path exists and is not a symlink"
    return 0
  fi

  run_cmd ln -s "$target" "$link_path"
}

install_skills() {
  local target_dir="$1"
  local label="$2"
  local mode="$3"
  ensure_dir "$target_dir"
  for skill in "$SKILLS_DIR"/*/; do
    local skill_name target
    skill_name="$(basename "$skill")"
    if [ "$mode" = "repo" ]; then
      target="../../.skills/$skill_name"
    else
      target="$SKILLS_DIR/$skill_name"
    fi
    link_skill "$target_dir" "$skill_name" "$target" "$mode"
  done
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY-RUN: checked skills → $label"
  else
    echo "✅  Installed skills → $label"
  fi
}

install_named_global_skills() {
  local target_dir="$1"
  local label="$2"
  shift 2
  ensure_dir "$target_dir"
  for skill_name in "$@"; do
    link_skill "$target_dir" "$skill_name" "$SKILLS_DIR/$skill_name" "global"
  done
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY-RUN: checked global skills → $label"
  else
    echo "✅  Installed global skills → $label"
  fi
}

install_bootstrap_link() {
  local link_path="$1"
  local target="$2"
  local label="$3"

  if [ -L "$link_path" ]; then
    local current_target
    current_target="$(readlink "$link_path")"
    if [ "$current_target" = "$target" ]; then
      echo "OK: $label"
      return 0
    fi
    if [ "$FORCE" = "1" ]; then
      run_cmd rm "$link_path"
    else
      echo "SKIP: $link_path points to non-owned target: $current_target"
      echo "      Review first, then rerun with --force if replacement is intended."
      return 0
    fi
  elif [ -e "$link_path" ]; then
    echo "SKIP: $link_path exists and is not a symlink"
    return 0
  fi

  run_cmd ln -s "$target" "$link_path"
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY-RUN: planned $label"
  else
    echo "✅  $label"
  fi
}

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║         obsidian-wiki — Agent Setup              ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── Step 1: .env ──────────────────────────────────────────────
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  run_cmd cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY-RUN: would create .env from .env.example"
  else
    echo "✅  Created .env from .env.example"
    echo "    → Edit .env and set OBSIDIAN_VAULT_PATH before using skills."
  fi
else
  echo "✅  .env already exists"
fi

# ── Step 1b: ~/.obsidian-wiki/config ─────────────────────────
GLOBAL_CONFIG_DIR="$HOME/.obsidian-wiki"
GLOBAL_CONFIG="$GLOBAL_CONFIG_DIR/config"

# Read vault path from .env if it's already set
VAULT_PATH=""
if [ -f "$SCRIPT_DIR/.env" ]; then
  # Strip quotes if present, but preserve the path (spaces or not)
  VAULT_PATH=$(grep -E '^OBSIDIAN_VAULT_PATH=' "$SCRIPT_DIR/.env" | cut -d'=' -f2- | sed 's/^"//;s/"$//')
fi

# If vault path is empty or placeholder, ask the user
if [ "$DRY_RUN" != "1" ] && { [ -z "$VAULT_PATH" ] || [ "$VAULT_PATH" = "/path/to/your/vault" ]; }; then
  echo ""
  read -p "  Where is your Obsidian vault? (absolute path): " VAULT_PATH
  if [ -n "$VAULT_PATH" ]; then
    # Escape the path for sed: replace '/' with '\/' and '"' with '\"'
    ESCAPED_PATH=$(printf '%s\n' "$VAULT_PATH" | sed -e 's/[\/&]/\\&/g' -e 's/"/\\"/g')
    # Update .env with quoted path to preserve spaces
    run_cmd sed -i.bak "s|^OBSIDIAN_VAULT_PATH=.*|OBSIDIAN_VAULT_PATH=\"$ESCAPED_PATH\"|" "$SCRIPT_DIR/.env"
    run_cmd rm -f "$SCRIPT_DIR/.env.bak"
  fi
fi

# Write global config only when requested. Quoted path preserves spaces.
if [ "$INSTALL_GLOBAL_CONFIG" = "1" ]; then
  write_global_config
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY-RUN: global config step checked at ~/.obsidian-wiki/config"
  else
    echo "ℹ️   Global config step checked at ~/.obsidian-wiki/config"
  fi
else
  echo "ℹ️   Skipped ~/.obsidian-wiki/config. Use --global-config or --global-skills to write it."
fi

# ── Step 1c: Bootstrap symlinks ──────────────────────────────
# .hermes.md → AGENTS.md  (Hermes resolves .hermes.md before AGENTS.md;
# a symlink keeps a single source of truth)
install_bootstrap_link "$SCRIPT_DIR/.hermes.md" "AGENTS.md" ".hermes.md → AGENTS.md"

# ── Step 2: Symlink skills into agent directories ─────────────
AGENT_DIRS=(
  ".claude/skills"
  ".cursor/skills"
  ".windsurf/skills"
  ".agents/skills"
)

for agent_dir in "${AGENT_DIRS[@]}"; do
  install_skills "$SCRIPT_DIR/$agent_dir" "$agent_dir/" "repo"
done

# ── Step 3: Install global skills ────────────────────────────
if [ "$INSTALL_GLOBAL_SKILLS" = "1" ]; then
  # ~/.claude/skills gets only the two portable skills (usable from any project)
  GLOBAL_SKILL_DIR="$HOME/.claude/skills"
  install_named_global_skills "$GLOBAL_SKILL_DIR" "~/.claude/skills/ (wiki-update, wiki-query)" "wiki-update" "wiki-query"

  # Steps 3b–3e: Install all skills for Gemini, Codex, Hermes, and generic agents
  # OpenClaw discovers skills from ~/.agents/skills/ (per docs.openclaw.ai/skills);
  # that path also covers OpenCode, Factory Droid, and any AGENTS.md-aware agent.
  install_skills "$HOME/.gemini/antigravity/skills" "~/.gemini/antigravity/skills/" "global"
  install_skills "$HOME/.codex/skills"              "~/.codex/skills/" "global"
  install_skills "$HOME/.hermes/skills"             "~/.hermes/skills/ (Hermes)" "global"
  install_skills "$HOME/.openclaw/skills"           "~/.openclaw/skills/ (OpenClaw managed)" "global"
  install_skills "$HOME/.agents/skills"             "~/.agents/skills/ (OpenClaw + generic)" "global"
else
  echo "ℹ️   Skipped global skill symlinks. Use --global-skills to install them."
fi

# ── Step 4: Summary ──────────────────────────────────────────
SKILL_COUNT=$(echo "$SKILLS_DIR"/*/  | tr ' ' '\n' | grep -c /)

echo ""
echo "───────────────────────────────────────────────────"
if [ "$DRY_RUN" = "1" ]; then
  echo " Setup dry-run complete!"
else
  echo " Setup complete!"
fi
echo ""
echo " Skills found:    $SKILL_COUNT"
echo " Local repo links: Claude Code, Cursor, Windsurf, generic agents"
if [ "$INSTALL_GLOBAL_SKILLS" = "1" ]; then
  if [ "$DRY_RUN" = "1" ]; then
    echo " Global links:     previewed for Claude, Codex, Gemini, Hermes, OpenClaw, generic agents"
  else
    echo " Global links:     configured for Claude, Codex, Gemini, Hermes, OpenClaw, generic agents"
  fi
else
  echo " Global links:     skipped; run with --global-skills after review"
fi
echo ""
echo " Bootstrap files:"
echo "   CLAUDE.md       → Claude Code"
echo "   GEMINI.md       → Gemini / Antigravity"
echo "   AGENTS.md       → Codex, OpenClaw, OpenCode, Droid"
echo "   .hermes.md      → Hermes"
echo "   .cursor/rules/  → Cursor"
echo "   .windsurf/rules/ → Windsurf"
echo "   .github/copilot-instructions.md → GitHub Copilot"
echo ""
echo " Next steps:"
echo "   1. Open this project in your agent"
echo "   2. Say: \"Set up my wiki\""
echo ""
if [ "$INSTALL_GLOBAL_SKILLS" = "1" ]; then
  echo " From any other project:"
  echo "   /wiki-update    → sync knowledge into your vault"
  echo "   /wiki-query    → ask questions against your wiki"
else
  echo " To use skills from other projects:"
  echo "   Review dry-run output, then run: bash setup.sh --global-skills"
fi
echo "───────────────────────────────────────────────────"
echo ""
