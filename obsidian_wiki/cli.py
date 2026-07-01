"""obsidian-wiki installer CLI.

Python port of ``setup.sh`` for the pip-installed package. The skill content
lives inside the installed package (``obsidian_wiki/_data/skills``) instead of a
cloned repo, so this wires supported skill profiles into AI agent discovery
paths and writes ``~/.obsidian-wiki/config`` so the skills resolve the vault
from any project.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from obsidian_wiki import __version__
from obsidian_wiki.write_guard import DRY_RUN_SCENARIOS, evaluate_operation, guarded_append_log_line

HOME = Path.home()
GLOBAL_CONFIG_DIR = HOME / ".obsidian-wiki"
GLOBAL_CONFIG = GLOBAL_CONFIG_DIR / "config"

# Skills usable from any project (no vault context needed beyond the global
# config). These are installed into Claude's global skill path; the full skill
# set remains available project-locally or through agents without tight startup
# skill budgets.
PORTABLE_SKILLS = ("wiki-update", "wiki-query")

# Codex includes every visible skill description in a small startup context
# budget. Keep the global Codex profile small and route uncommon work through
# these entrypoints or project-local skills.
CODEX_MINIMAL_SKILLS = (
    "impl-validator",
    "wiki-capture",
    "wiki-context-pack",
    "wiki-ingest",
    "wiki-lint",
    "wiki-query",
    "wiki-setup",
    "wiki-stage-commit",
    "wiki-status",
    "wiki-tools",
    "wiki-update",
    "wiki-write-guard",
)
CODEX_SKILL_PROFILES: dict[str, tuple[str, ...] | None] = {
    "minimal": CODEX_MINIMAL_SKILLS,
    "full": None,
}
DEFAULT_CODEX_PROFILE = "minimal"


# ── Data resolution ──────────────────────────────────────────────────────────
# Works for both a built wheel (data under <pkg>/_data) and an editable/source
# checkout (data at the repo root next to the package).
def _pkg_dir() -> Path:
    return Path(__file__).resolve().parent


def skills_dir() -> Path:
    """Return the directory holding the bundled skill folders."""
    for cand in (_pkg_dir() / "_data" / "skills", _pkg_dir().parent / ".skills"):
        if cand.is_dir():
            return cand
    raise FileNotFoundError(
        "Could not locate bundled skills. Reinstall obsidian-wiki "
        "(`pip install --force-reinstall obsidian-wiki`)."
    )


def bootstrap_dir() -> Path | None:
    """Return the directory containing agent bootstrap context files.

    For a wheel this is ``_data/bootstrap``; for a source checkout the files are
    spread across the repo root, so we return the repo root and resolve each
    file via the repo-relative layout in ``_bootstrap_files``.
    """
    built = _pkg_dir() / "_data" / "bootstrap"
    if built.is_dir():
        return built
    repo = _pkg_dir().parent
    if (repo / "AGENTS.md").is_file():
        return repo
    return None


def list_skills() -> list[str]:
    return sorted(p.name for p in skills_dir().iterdir() if p.is_dir())


# ── Skill installation ───────────────────────────────────────────────────────
def install_skills(
    target_dir: Path,
    label: str,
    *,
    subset: tuple[str, ...] | None = None,
    prune_unselected: bool = False,
    mode: str = "symlink",
    quiet: bool = False,
) -> int:
    """Install bundled skills into *target_dir*. Returns the count installed."""
    src_root = skills_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    if prune_unselected and subset is not None:
        selected = set(subset)
        for skill in sorted(p for p in src_root.iterdir() if p.is_dir()):
            if skill.name in selected:
                continue
            link_path = target_dir / skill.name
            if link_path.is_symlink() or link_path.is_file():
                link_path.unlink()
            elif link_path.is_dir() and (link_path / "SKILL.md").exists():
                shutil.rmtree(link_path)

    installed = 0
    for skill in sorted(p for p in src_root.iterdir() if p.is_dir()):
        name = skill.name
        if subset is not None and name not in subset:
            continue
        link_path = target_dir / name

        if link_path.is_symlink() or link_path.is_file():
            link_path.unlink()
        elif link_path.is_dir():
            # A real directory we previously copied here is safe to replace;
            # anything else is the user's and we leave it alone.
            if (link_path / "SKILL.md").exists():
                shutil.rmtree(link_path)
            else:
                print(f"   ⚠️  {link_path} is not a managed skill, skipping")
                continue

        if mode == "symlink":
            link_path.symlink_to(skill, target_is_directory=True)
        else:  # copy
            shutil.copytree(skill, link_path)

        if not (link_path / "SKILL.md").exists():
            raise RuntimeError(f"broken skill install: {link_path} -> {skill}")
        installed += 1

    if not quiet:
        print(f"✅  Installed {installed} skills → {label}")
    return installed


# Agents whose skills directory lives under $HOME. Tuple shape:
# (path-under-home, label, subset, prune_unselected).
def global_agent_dirs(codex_profile: str) -> list[tuple[str, str, tuple[str, ...] | None, bool]]:
    codex_subset = CODEX_SKILL_PROFILES[codex_profile]
    codex_label = (
        "~/.codex/skills/ (Codex, minimal profile)"
        if codex_profile == "minimal"
        else "~/.codex/skills/ (Codex, full profile)"
    )
    return [
        (".claude/skills", "~/.claude/skills/ (Claude Code, portable skills)", PORTABLE_SKILLS, True),
        (".gemini/skills", "~/.gemini/skills/ (Gemini CLI)", None, False),
        (".gemini/antigravity/skills", "~/.gemini/antigravity/skills/ (Antigravity, legacy)", None, False),
        (".codex/skills", codex_label, codex_subset, codex_subset is not None),
        (".hermes/skills", "~/.hermes/skills/ (Hermes default)", None, False),
        (".openclaw/skills", "~/.openclaw/skills/ (OpenClaw)", None, False),
        (".copilot/skills", "~/.copilot/skills/ (GitHub Copilot CLI)", None, False),
        (".trae/skills", "~/.trae/skills/ (Trae)", None, False),
        (".trae-cn/skills", "~/.trae-cn/skills/ (Trae CN)", None, False),
        (".kiro/skills", "~/.kiro/skills/ (Kiro CLI)", None, False),
        (".pi/agent/skills", "~/.pi/agent/skills/ (Pi)", None, False),
        (".agents/skills", "~/.agents/skills/ (OpenCode, Aider, Droid, generic)", None, False),
    ]


def install_global_skills(mode: str, codex_profile: str) -> None:
    for rel, label, subset, prune_unselected in global_agent_dirs(codex_profile):
        install_skills(
            HOME / rel,
            label,
            subset=subset,
            prune_unselected=prune_unselected,
            mode=mode,
        )
    _install_hermes_profiles(mode)


def _install_hermes_profiles(mode: str) -> None:
    """Mirror setup.sh: install into the active and all named Hermes profiles."""
    hermes_home = os.environ.get("HERMES_HOME")
    handled: set[Path] = set()
    if hermes_home:
        hp = Path(hermes_home).expanduser()
        if hp != HOME / ".hermes":
            install_skills(hp / "skills", f"{hp}/skills/ (Hermes active profile)", mode=mode)
            handled.add(hp)
    profiles = HOME / ".hermes" / "profiles"
    if profiles.is_dir():
        for prof in sorted(p for p in profiles.iterdir() if p.is_dir()):
            if prof in handled:
                continue
            install_skills(
                prof / "skills",
                f"~/.hermes/profiles/{prof.name}/skills/ (Hermes profile: {prof.name})",
                mode=mode,
            )


# ── Project-local install (opt-in) ───────────────────────────────────────────
PROJECT_AGENT_DIRS = [
    (".claude/skills", "Claude Code"),
    (".cursor/skills", "Cursor"),
    (".windsurf/skills", "Windsurf"),
    (".agents/skills", "OpenCode / generic"),
    (".pi/skills", "Pi"),
    (".kiro/skills", "Kiro"),
]

# (bootstrap-relative source path, destination relative to project dir).
# The source path is resolved against bootstrap_dir() for a wheel, or mapped to
# the repo layout for a source checkout (see _resolve_bootstrap_src).
BOOTSTRAP_FILES = [
    ("AGENTS.md", "AGENTS.md"),
    ("cursor/rules/obsidian-wiki.mdc", ".cursor/rules/obsidian-wiki.mdc"),
    ("windsurf/rules/obsidian-wiki.md", ".windsurf/rules/obsidian-wiki.md"),
    ("kiro/steering/obsidian-wiki.md", ".kiro/steering/obsidian-wiki.md"),
    ("agent/rules/obsidian-wiki.md", ".agent/rules/obsidian-wiki.md"),
    ("agent/workflows/obsidian-wiki.md", ".agent/workflows/obsidian-wiki.md"),
    ("github/copilot-instructions.md", ".github/copilot-instructions.md"),
]

# AGENTS.md aliases created as symlinks within the project (single source).
AGENTS_ALIASES = ("CLAUDE.md", "GEMINI.md", ".hermes.md")


def _resolve_bootstrap_src(boot_root: Path, rel: str) -> Path | None:
    """Resolve a bootstrap source path under a wheel layout or repo layout."""
    built = boot_root / rel
    if built.exists():
        return built
    # Source checkout: boot_root is the repo root; files use the repo layout.
    repo_rel = {
        "AGENTS.md": "AGENTS.md",
        "cursor/rules/obsidian-wiki.mdc": ".cursor/rules/obsidian-wiki.mdc",
        "windsurf/rules/obsidian-wiki.md": ".windsurf/rules/obsidian-wiki.md",
        "kiro/steering/obsidian-wiki.md": ".kiro/steering/obsidian-wiki.md",
        "agent/rules/obsidian-wiki.md": ".agent/rules/obsidian-wiki.md",
        "agent/workflows/obsidian-wiki.md": ".agent/workflows/obsidian-wiki.md",
        "github/copilot-instructions.md": ".github/copilot-instructions.md",
    }.get(rel)
    if repo_rel and (boot_root / repo_rel).exists():
        return boot_root / repo_rel
    return None


def install_project(project_dir: Path, mode: str) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁  Installing project-local files → {project_dir}")
    for rel, _label in PROJECT_AGENT_DIRS:
        install_skills(project_dir / rel, f"{rel}/", mode=mode)

    boot_root = bootstrap_dir()
    if boot_root is None:
        print("   ⚠️  Bootstrap files not found in package; skipping context files")
        return

    for rel, dest in BOOTSTRAP_FILES:
        src = _resolve_bootstrap_src(boot_root, rel)
        if src is None:
            continue
        dst = project_dir / dest
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.is_symlink() or dst.exists():
            if dst.is_dir() and not dst.is_symlink():
                continue
            dst.unlink()
        shutil.copyfile(src, dst)
    print("✅  Installed bootstrap context files (AGENTS.md, rules, workflows)")

    # AGENTS.md aliases as relative symlinks (copy fallback for symlink-hostile FS).
    for alias in AGENTS_ALIASES:
        link = project_dir / alias
        if link.is_symlink() or link.exists():
            link.unlink()
        try:
            link.symlink_to("AGENTS.md")
        except OSError:
            shutil.copyfile(project_dir / "AGENTS.md", link)
    print(f"✅  Linked AGENTS.md aliases ({', '.join(AGENTS_ALIASES)})")


# ── Config ───────────────────────────────────────────────────────────────────
def _read_config_value(key: str) -> str:
    if not GLOBAL_CONFIG.is_file():
        return ""
    for line in GLOBAL_CONFIG.read_text().splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"')
    return ""


def resolve_vault_path(cli_vault: str | None) -> str:
    if cli_vault:
        return os.path.expanduser(cli_vault)
    existing = _read_config_value("OBSIDIAN_VAULT_PATH")
    if existing and existing != "/path/to/your/vault":
        return existing
    if sys.stdin.isatty():
        try:
            entered = input("  Where is your Obsidian vault? (absolute path): ").strip()
        except EOFError:
            entered = ""
        if entered:
            return os.path.expanduser(entered)
    return existing


def write_config(vault_path: str, codex_profile: str) -> None:
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # OBSIDIAN_WIKI_REPO points at the bundled data root so skills that reference
    # framework assets (templates, references) can find them post-install.
    repo_root = skills_dir().parent
    GLOBAL_CONFIG.write_text(
        f'OBSIDIAN_VAULT_PATH="{vault_path}"\n'
        f'OBSIDIAN_WIKI_REPO="{repo_root}"\n'
        f'OBSIDIAN_WIKI_VERSION="{__version__}"\n'
        f'OBSIDIAN_CODEX_SKILL_PROFILE="{codex_profile}"\n'
    )
    print(f"✅  Global config written to {GLOBAL_CONFIG}")


def resolve_codex_profile(cli_profile: str | None = None) -> str:
    profile = (
        cli_profile
        or os.environ.get("OBSIDIAN_CODEX_SKILL_PROFILE")
        or _read_config_value("OBSIDIAN_CODEX_SKILL_PROFILE")
        or DEFAULT_CODEX_PROFILE
    )
    if profile not in CODEX_SKILL_PROFILES:
        print(
            f"⚠️  Unknown OBSIDIAN_CODEX_SKILL_PROFILE={profile!r}; using {DEFAULT_CODEX_PROFILE!r}.",
            file=sys.stderr,
        )
        return DEFAULT_CODEX_PROFILE
    return profile


def _check_stale() -> None:
    """Warn if the installed version doesn't match when setup last ran, or if skills are missing."""
    if not GLOBAL_CONFIG.is_file():
        print(
            f"⚠️  obsidian-wiki {__version__} is installed but setup has never been run.\n"
            f"   Run: obsidian-wiki setup --vault /path/to/your/vault",
            file=sys.stderr,
        )
        return

    setup_version = _read_config_value("OBSIDIAN_WIKI_VERSION")
    if setup_version and setup_version != __version__:
        print(
            f"⚠️  obsidian-wiki upgraded {setup_version} → {__version__} but setup hasn't been re-run.\n"
            f"   New skills won't be available until you run: obsidian-wiki setup",
            file=sys.stderr,
        )
        return

    bundled = set(list_skills())
    codex_profile = resolve_codex_profile()
    for rel, label, subset, _prune_unselected in global_agent_dirs(codex_profile):
        expected = set(subset or bundled)
        agent_dir = HOME / rel
        if not agent_dir.is_dir():
            continue
        installed = {p.name for p in agent_dir.iterdir() if p.is_dir()}
        missing = expected - installed
        extra = (installed & bundled) - expected
        if missing or extra:
            detail = []
            if missing:
                detail.append(
                    f"{len(missing)} missing "
                    f"(e.g. {', '.join(sorted(missing)[:3])}{', ...' if len(missing) > 3 else ''})"
                )
            if extra:
                detail.append(
                    f"{len(extra)} extra bundled "
                    f"(e.g. {', '.join(sorted(extra)[:3])}{', ...' if len(extra) > 3 else ''})"
                )
            print(
                f"⚠️  Skill profile drift in {label}: {'; '.join(detail)}.\n"
                f"   Run: obsidian-wiki setup",
                file=sys.stderr,
            )
            return


# ── Commands ─────────────────────────────────────────────────────────────────
def cmd_setup(args: argparse.Namespace) -> int:
    mode = "copy" if args.copy else "symlink"
    codex_profile = resolve_codex_profile(args.codex_profile)
    print("\n╔══════════════════════════════════════════════════╗")
    print("║         obsidian-wiki — Agent Setup              ║")
    print("╚══════════════════════════════════════════════════╝\n")

    vault_path = resolve_vault_path(args.vault)
    write_config(vault_path, codex_profile)
    if not vault_path:
        print("    → Vault path not set yet. Re-run with `--vault /path/to/vault`")
        print("      or edit OBSIDIAN_VAULT_PATH in ~/.obsidian-wiki/config.")

    if not args.project_only:
        print()
        install_global_skills(mode, codex_profile)

    if args.project is not None:
        project_dir = Path(args.project or os.getcwd()).expanduser().resolve()
        install_project(project_dir, mode)

    n = len(list_skills())
    print("\n───────────────────────────────────────────────────")
    print(" Setup complete!\n")
    print(f" Bundled skills:   {n}  (mode: {mode})")
    print(f" Codex profile:    {codex_profile} ({len(CODEX_SKILL_PROFILES[codex_profile] or list_skills())} global skills)")
    if vault_path:
        print(f" Vault:            {vault_path}")
    print("\n Next steps:")
    print("   1. Open a project in your agent")
    print('   2. Say: "set up my wiki"\n')
    print(" From any project:")
    print("   /wiki-update    → sync knowledge into your vault")
    print("   /wiki-query     → ask questions against your wiki")
    print("───────────────────────────────────────────────────\n")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    for name in list_skills():
        print(name)
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    bundled = list_skills()
    codex_profile = resolve_codex_profile()
    print(f"obsidian-wiki {__version__}")
    print(f"skills:    {skills_dir()}")
    boot = bootstrap_dir()
    print(f"bootstrap: {boot if boot else '(not found)'}")
    print(f"config:    {GLOBAL_CONFIG}{'' if GLOBAL_CONFIG.exists() else ' (not written yet)'}")
    if GLOBAL_CONFIG.exists():
        vp = _read_config_value("OBSIDIAN_VAULT_PATH")
        setup_ver = _read_config_value("OBSIDIAN_WIKI_VERSION")
        setup_codex_profile = _read_config_value("OBSIDIAN_CODEX_SKILL_PROFILE")
        print(f"vault:     {vp or '(unset)'}")
        print(f"setup ran: {setup_ver or '(never)'}")
        profile_note = (
            f"{codex_profile} (config: {setup_codex_profile})"
            if setup_codex_profile and setup_codex_profile != codex_profile
            else codex_profile
        )
        print(f"codex profile: {profile_note}")
    print(f"bundled skills: {len(bundled)}")
    print()
    print("Agent skill install status:")
    bundled_set = set(bundled)
    for rel, label, subset, _prune_unselected in global_agent_dirs(codex_profile):
        agent_dir = HOME / rel
        if not agent_dir.is_dir():
            print(f"  {label}: not installed")
            continue
        expected = set(subset or bundled)
        installed = {p.name for p in agent_dir.iterdir() if p.is_dir()}
        wiki_installed = installed & expected
        missing = expected - installed
        extra = (installed & bundled_set) - expected
        status = "✅" if not missing and not extra else "⚠️ "
        print(f"  {status} {label}: {len(wiki_installed)}/{len(expected)}", end="")
        notes = []
        if missing:
            notes.append(f"{len(missing)} missing")
        if extra:
            notes.append(f"{len(extra)} extra bundled")
        if notes:
            print(f"  ({'; '.join(notes)}; run: obsidian-wiki setup)", end="")
        print()
    _check_stale()
    return 0


def cmd_guard_dry_run(args: argparse.Namespace) -> int:
    if args.operation_json:
        operation = json.loads(Path(args.operation_json).read_text(encoding="utf-8"))
        scenarios = [(args.operation_json, operation)]
    else:
        selected = args.scenario or sorted(DRY_RUN_SCENARIOS)
        scenarios = [(name, DRY_RUN_SCENARIOS[name]) for name in selected]

    results = []
    for name, operation in scenarios:
        decision = evaluate_operation(operation)
        results.append({"scenario": name, "operation": operation, **decision.as_dict()})

    if args.format == "json":
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for result in results:
            print(f"{result['scenario']}: {result['decision']} - {result['reason']}")
            print(f"  action: {result['required_action']}")
    if args.fail_on_non_approve and any(result["decision"] != "approve" for result in results):
        return 2
    return 0


def cmd_guarded_log_append(args: argparse.Namespace) -> int:
    operation = json.loads(Path(args.operation_json).read_text(encoding="utf-8"))
    result = guarded_append_log_line(Path(args.vault).expanduser().resolve(), operation, args.line)

    if args.format == "json":
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"{result.decision.decision}: wrote={str(result.wrote).lower()}")
        print(f"  target: {result.target_path}")
        print(f"  reason: {result.decision.reason}")
    return 0 if result.wrote else 2


# ── Argument parsing ─────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="obsidian-wiki",
        description="Install the LLM-Wiki agent skills into your AI coding agents.",
    )
    p.add_argument("-V", "--version", action="version", version=f"obsidian-wiki {__version__}")
    sub = p.add_subparsers(dest="command")

    sp = sub.add_parser("setup", help="install skills into your agents and write config (default)")
    _add_setup_args(sp)
    sp.set_defaults(func=cmd_setup)

    lp = sub.add_parser("list", help="list bundled skills")
    lp.set_defaults(func=cmd_list)

    ip = sub.add_parser("info", help="show install paths, version, and config")
    ip.set_defaults(func=cmd_info)

    gp = sub.add_parser("guard-dry-run", help="evaluate wiki-write-guard scenarios without writing")
    gp.add_argument(
        "--scenario",
        choices=sorted(DRY_RUN_SCENARIOS),
        action="append",
        help="built-in scenario to evaluate; may be repeated; defaults to all",
    )
    gp.add_argument("--operation-json", metavar="PATH", help="evaluate one proposed operation JSON file")
    gp.add_argument("--format", choices=("text", "json"), default="text")
    gp.add_argument(
        "--fail-on-non-approve",
        action="store_true",
        help="return exit code 2 if any evaluated operation is not approved",
    )
    gp.set_defaults(func=cmd_guard_dry_run)

    wap = sub.add_parser(
        "guarded-log-append",
        help="append one log line to a vault only after write-guard approval",
    )
    wap.add_argument("--vault", required=True, metavar="PATH", help="vault directory containing log.md")
    wap.add_argument("--operation-json", required=True, metavar="PATH", help="proposed operation JSON file")
    wap.add_argument("--line", required=True, help="single physical log line to append")
    wap.add_argument("--format", choices=("text", "json"), default="text")
    wap.set_defaults(func=cmd_guarded_log_append)

    return p


def _add_setup_args(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--vault", metavar="PATH", help="absolute path to your Obsidian vault")
    sp.add_argument(
        "--project",
        nargs="?",
        const="",
        default=None,
        metavar="DIR",
        help="also install project-local skills + bootstrap files into DIR "
        "(defaults to the current directory if no DIR given)",
    )
    sp.add_argument(
        "--project-only",
        action="store_true",
        help="skip the global agent install (use with --project)",
    )
    sp.add_argument(
        "--copy",
        action="store_true",
        help="copy skill files instead of symlinking to the installed package",
    )
    sp.add_argument(
        "--codex-profile",
        choices=sorted(CODEX_SKILL_PROFILES),
        default=None,
        help=(
            "skills to install globally for Codex; default is minimal to avoid "
            "Codex startup skill-budget pressure"
        ),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    argv = list(sys.argv[1:] if argv is None else argv)
    # No subcommand → default to `setup` (the common case).
    if not argv or (argv[0].startswith("-") and argv[0] not in ("-h", "--help", "-V", "--version")):
        argv = ["setup", *argv]
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    # Warn about stale installs on every command except `setup` (which fixes it)
    # and `info` (which calls _check_stale itself with richer output).
    if getattr(args, "command", None) not in ("setup", "info", "guard-dry-run", "guarded-log-append", None):
        _check_stale()
    try:
        return args.func(args)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
