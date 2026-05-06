# review-agent

A small CLI code-review agent. Pipes a git diff to Claude Opus 4.7 and prints
a structured review. The agent can call a `read_file` tool to fetch
surrounding source when the diff hunks don't show enough context.

## Install

```sh
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Use

```sh
# Review staged changes (default)
python review_agent.py

# Review the current branch against main
python review_agent.py --base main

# Review unstaged working-tree changes
python review_agent.py --unstaged

# Review a saved diff file
python review_agent.py --diff my-changes.diff
```

## How it works

- Adaptive thinking on Claude Opus 4.7 (`claude-opus-4-7`).
- Prompt caching on the system prompt so each tool roundtrip reuses the prefix.
- One tool: `read_file(path, start_line?, end_line?)`, sandboxed to the
  current git repository.
- Streams output incrementally; logs each tool call to stderr so you can see
  what the agent looked at.

## Output

Findings are grouped by severity (BLOCKER / MAJOR / MINOR / NIT) with a
`file:line` cite, the issue, and a suggested fix. Ends with a one-paragraph
summary covering correctness, security, and maintainability.
