from __future__ import annotations

from obsidian_wiki import cli


def installed_skill_names(target):
    return sorted(p.name for p in target.iterdir() if p.is_dir())


def test_codex_minimal_profile_is_bundled_and_smaller_than_full() -> None:
    bundled = set(cli.list_skills())
    minimal = set(cli.CODEX_MINIMAL_SKILLS)

    assert minimal <= bundled
    assert "wiki-query" in minimal
    assert "wiki-write-guard" in minimal
    assert "impl-validator" in minimal
    assert "wiki-tools" in minimal
    assert len(minimal) < len(bundled)


def test_wiki_tools_router_targets_existing_skills() -> None:
    text = (cli.skills_dir() / "wiki-tools" / "SKILL.md").read_text(encoding="utf-8")
    bundled = set(cli.list_skills())
    targets = {
        token.strip("`")
        for token in text.replace("|", " ").split()
        if token.startswith("`") and token.endswith("`") and "/" not in token
    }
    routed_targets = {target for target in targets if target in bundled and target != "wiki-tools"}

    assert "wiki-export" in routed_targets
    assert "wiki-rebuild" in routed_targets
    assert "wiki-history-ingest" in routed_targets
    assert "vault-skill-factory" in routed_targets
    assert routed_targets <= bundled


def test_global_agent_dirs_use_codex_minimal_profile_by_default_shape() -> None:
    dirs = cli.global_agent_dirs("minimal")
    codex = [entry for entry in dirs if entry[0] == ".codex/skills"][0]
    claude = [entry for entry in dirs if entry[0] == ".claude/skills"][0]

    assert codex[2] == cli.CODEX_MINIMAL_SKILLS
    assert codex[3] is True
    assert claude[2] == cli.PORTABLE_SKILLS
    assert claude[3] is True


def test_install_skills_prunes_bundled_skills_outside_subset(tmp_path) -> None:
    target = tmp_path / "skills"

    cli.install_skills(target, "test", mode="symlink", quiet=True)
    assert len(installed_skill_names(target)) == len(cli.list_skills())

    subset = ("wiki-query", "wiki-update")
    cli.install_skills(
        target,
        "test",
        subset=subset,
        prune_unselected=True,
        mode="symlink",
        quiet=True,
    )

    assert installed_skill_names(target) == sorted(subset)


def test_setup_parser_exposes_codex_profile_choice() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(["setup", "--codex-profile", "full"])

    assert args.command == "setup"
    assert args.codex_profile == "full"
