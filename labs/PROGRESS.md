# labs/ — overnight build log

> Durable state for the autonomous overnight `/loop`. **Read this first on every
> wakeup** — context may have been summarized, but this file is the source of
> truth for what's built, what's next, and the rules.

## Mission

Research wild, ambitious, trending AI-agent ideas and ship them as working MVPs
into `labs/`, continuously through the night. Go wild — but ship things that
*actually run*.

## Hard rules (do not violate)

1. **Offline-first, stdlib-only to RUN.** No MVP may *require* an API key or any
   pip install to execute its demo and tests. `anthropic`/`pydantic` are
   optional enhancements, imported lazily. The container is ephemeral and has no
   `ANTHROPIC_API_KEY`, so offline is the demonstrable path.
2. **Every MVP ships with: a README, a runnable CLI/demo, and `unittest` tests
   that pass.** Verify before committing.
3. **Determinism.** Use `labs/_kernel/text.py` (`rng`, `stable_seed`) for any
   randomness so demos/tests are reproducible. Never use bare `hash()` (salted).
4. **Reuse `labs/_kernel`** (`Brain` abstraction, text utils) rather than
   duplicating.
5. **Commit + push after each MVP** to `claude/vibrant-carson-s0hqd6`. Small,
   green commits.
6. Do **not** open a PR (not requested). Do **not** touch the existing
   `agents/` pharma platform code.

## Status board

| # | MVP | Idea / inspiration | Status |
| --- | --- | --- | --- |
| 0 | `_kernel` | shared Brain + deterministic text utils | ✅ done |
| 1 | `agent_swarm` | multi-agent debate firm (TradingAgents, generalized) | ✅ done — 9 tests green |
| 2 | `agent_memory` | an agent that *grows with you*: semantic+episodic+working memory, reflection (Hermes/generative-agents) | ✅ done — 10 tests green |
| 3 | `jailbreak_gauntlet` | defensive agentic-security harness: prompt-injection probes vs. a defended agent, scored (LLM4Pentest) | ✅ done — 11 tests green, guard grades A- |
| 4 | `prompt_evolver` | evolutionary/genetic prompt optimizer over a task suite (DSPy/evo-prompt) | ✅ done — 10 tests green |
| 5 | `tiny_town` | Smallville-style generative-agent simulation (reuses agent_memory!) | ✅ done — 11 tests green |
| 6 | `agent_os` | micro agent-OS: scheduler + task queue + blackboard (AutoGPT platform) | ✅ done — 12 tests green |
| 7 | `repo_cartographer` | map a repo into a knowledge graph + answer questions | ⏳ next |

(Append new ideas here as they're found. Keep the table honest.)

## How to run what exists

```sh
python -m labs.agent_swarm.demo                 # tour
python -m labs.agent_swarm.cli --list           # panels
python -m unittest discover -s labs -t . -p 'test_*.py'   # all lab tests
```

## Next steps (for the next wakeup)

- Build MVP #7 `repo_cartographer`. Then research fresh ideas (#8+).
- After each: run its tests + `unittest discover -s labs -t .`, update this table,
  commit, push.
- If you hit a usage/time limit: stop, and the loop will re-check on its
  schedule. Re-read this file when you resume.
