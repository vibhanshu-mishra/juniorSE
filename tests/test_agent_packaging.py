import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_claude_project_instructions_exist_and_are_concise():
    path = ROOT / "CLAUDE.md"
    assert path.exists()
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 200
    text = "\n".join(lines)
    assert "no silent" in text.lower()
    assert "pytest" in text.lower()


def test_plugin_manifest_exposes_all_skill_roots():
    path = ROOT / ".claude-plugin" / "plugin.json"
    assert path.exists()
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["name"] == "juniorse"
    assert manifest["version"] == "1.6.0"
    assert manifest["skills"] == [
        "./plugin-skills/",
        "./skills/core/",
        "./skills/loads/",
        "./skills/steel/",
    ]


def test_marketplace_installs_plugin_from_repo_root():
    path = ROOT / ".claude-plugin" / "marketplace.json"
    assert path.exists()
    marketplace = json.loads(path.read_text(encoding="utf-8"))
    assert marketplace["name"] == "juniorse"
    plugins = marketplace["plugins"]
    assert len(plugins) == 1
    assert plugins[0]["name"] == "juniorse"
    assert plugins[0]["source"] == "."


def test_router_skill_exists_and_names_all_current_skill_modules():
    router = ROOT / "plugin-skills" / "juniorse" / "SKILL.md"
    assert router.exists()
    text = router.read_text(encoding="utf-8")
    assert re.search(r"(?m)^name:\s*juniorse\s*$", text)

    expected = []
    for category in ("core", "loads", "steel"):
        category_dir = ROOT / "skills" / category
        expected.extend(sorted(p.name for p in category_dir.iterdir() if (p / "SKILL.md").exists()))

    for skill_name in expected:
        assert skill_name in text, f"router does not mention {skill_name}"


def test_agents_md_exists_for_cross_agent_contributors():
    path = ROOT / "AGENTS.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8").lower()
    assert "juniorse" in text
    assert "skill.md" in text
    assert "rules.yaml" in text


def test_readme_contains_claude_plugin_install_commands():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "claude plugin marketplace add vibhanshu-mishra/juniorSE" in text
    assert "claude plugin install juniorse@juniorse" in text
    assert "/juniorse:juniorse" in text
