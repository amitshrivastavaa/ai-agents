# review-agent

CLI code-review agent for git diffs. Pipes a diff to Claude Opus 4.7 and
streams a structured review. The agent can call a `read_file` tool to fetch
surrounding source when the diff hunks don't show enough context.

## Use

From the repo root:

```sh
# Review staged changes (default)
python -m agents.review.agent

# Review the current branch against main
python -m agents.review.agent --base main

# Review unstaged working-tree changes
python -m agents.review.agent --unstaged

# Review a saved diff file
python -m agents.review.agent --diff my-changes.diff
```

## How it works

- Adaptive thinking on Claude Opus 4.7 (`claude-opus-4-7`).
- Prompt caching on the system prompt so each tool roundtrip reuses the prefix.
- One tool: `read_file(path, start_line?, end_line?)`, sandboxed to the
  current git repository (shared in `lib/tools.py`).
- Streams output incrementally; logs each tool call to stderr so you can see
  what the agent looked at.

## Output

Findings are grouped by severity (BLOCKER / MAJOR / MINOR / NIT) with a
`file:line` cite, the issue, and a suggested fix. Ends with a one-paragraph
summary covering correctness, security, and maintainability.
