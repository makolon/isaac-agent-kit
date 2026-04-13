# isaac-agent-kit

`isaac-agent-kit` bootstraps repository instructions for coding agents. It currently ships a generic Python profile and an `isaaclab` profile for Isaac Lab based repositories.

## Usage

Render the Isaac Lab profile into the current repository:

```bash
uvx isaac-agent-kit init --profile isaaclab
```

Render the generic Python profile instead:

```bash
uvx isaac-agent-kit init --profile base
```

Inspect available profiles:

```bash
uvx isaac-agent-kit profiles
```

You can also wire the generator into a downstream Pixi workspace with a task such as:

```toml
[tasks]
init-agent = "uvx isaac-agent-kit init --profile isaaclab"
```

## Generated Files

The `base` profile renders:

- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`
- `.github/instructions/python.instructions.md`
- `.github/instructions/python-tests.instructions.md`

The `isaaclab` profile renders all of the above and adds Isaac Lab specific:

- `.github/instructions/isaaclab.instructions.md`
- `.github/instructions/isaaclab-validation.instructions.md`
- `.github/agents/task-author.agent.md`
- `.github/agents/actuator-debugger.agent.md`
- `.github/skills/isaaclab-task-author/SKILL.md`
- `.github/skills/isaaclab-actuator-debugging/SKILL.md`

## Design Notes

The common templates are intentionally short and reusable across agent systems:

- `AGENTS.md` is the shared repository-wide instruction file.
- `CLAUDE.md` delegates back to `AGENTS.md` so Claude Code style memory files stay in sync.
- GitHub Copilot specific instructions are split into repository-wide instructions, path-specific instructions, custom agents, and skills.

The Isaac Lab profile adds guardrails around common failure modes in simulator-heavy repositories, especially config-vs-runtime separation, eager simulator imports, and actuator debugging.

## References

These templates were informed by public documentation and examples:

- GitHub Copilot customization library and repository instructions: <https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot>
- GitHub Copilot testing automation example for path-specific instructions: <https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/customization-library/custom-instructions/testing-automation>
- Anthropic Claude Code memory files (`CLAUDE.md`): <https://docs.anthropic.com/en/docs/claude-code/memory>
- Isaac Lab contribution guidelines and code-structure notes: <https://isaac-sim.github.io/IsaacLab/develop/source/refs/contributing.html>
- Pixi task runner basics: <https://pixi.sh/dev/getting_started/>
