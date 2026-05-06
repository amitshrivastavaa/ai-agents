# ai-agents

A collection of small, shippable AI agents built on the Anthropic API.

## Layout

```
agents/<name>/   # one directory per agent (CLI entry + agent-specific README)
lib/             # shared tool definitions, sandboxing, repo helpers
```

## Agents

| Agent | Description |
| --- | --- |
| [`review`](agents/review/) | CLI code-review agent for git diffs. Streams a structured review with severity-grouped findings. |

## Install

```sh
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Run

From the repo root:

```sh
python -m agents.<name>.agent [args...]
```

For example: `python -m agents.review.agent --base main`. See each agent's
README for its CLI.

## Conventions

- Each agent lives in `agents/<name>/` with an `agent.py` entry point and a
  `README.md` documenting the CLI.
- Shared tool schemas and executors live in `lib/`. New agents should reuse
  them rather than duplicating sandboxing logic.
- Default model: `claude-opus-4-7` with adaptive thinking and prompt
  caching on the system prompt.
