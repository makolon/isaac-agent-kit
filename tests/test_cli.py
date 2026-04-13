from __future__ import annotations

from pathlib import Path

import pytest

from isaac_agent_kit.cli import build_file_plan, main


def test_profiles_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["profiles"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "base" in captured.out
    assert "isaaclab" in captured.out


def test_isaaclab_init_writes_expected_files(tmp_path: Path) -> None:
    exit_code = main(["init", "--profile", "isaaclab", "--target", str(tmp_path)])

    assert exit_code == 0
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".github" / "copilot-instructions.md").exists()
    assert (tmp_path / ".github" / "agents" / "actuator-debugger.agent.md").exists()
    assert (tmp_path / ".github" / "skills" / "isaaclab-task-author" / "SKILL.md").exists()
    assert "Agent Guide For" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")


def test_init_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("existing\n", encoding="utf-8")

    exit_code = main(["init", "--profile", "base", "--target", str(tmp_path)])

    assert exit_code == 1
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "existing\n"


def test_build_file_plan_overlays_profile_specific_templates() -> None:
    plan = {item.relative_path.as_posix(): item for item in build_file_plan("isaaclab", {"repo_name": "demo"})}

    assert plan["AGENTS.md"].source_layer == "isaaclab"
    assert ".github/instructions/python.instructions.md" in plan
