# labs/ — a research lab of wild AI-agent MVPs

An overnight, autonomously-built collection of small but *working* MVPs, each
inspired by a trending idea in the AI-agent space. Every MVP is self-contained,
runs **offline with the Python standard library alone** (no API key, nothing to
install), and upgrades to a real model when `ANTHROPIC_API_KEY` is set.

> This directory is intentionally separate from the production `agents/` pharma
> platform — it's an experimentation sandbox. See
> [`PROGRESS.md`](PROGRESS.md) for the running build log.

## The MVPs

| MVP | What it is | Inspired by |
| --- | --- | --- |
| [`agent_swarm`](agent_swarm/) | A panel of specialist agents debates your question over three rounds and votes; a moderator synthesizes a decision record with confidence, consensus, and dissent. | the viral *TradingAgents* LLM trading firm |
| [`agent_memory`](agent_memory/) | A persistent memory that grows with you: an episodic stream you can search by meaning (relevance × importance × recency), reflected into semantic insights over time. | the "agent that grows with you" wave; Generative Agents |
| [`jailbreak_gauntlet`](jailbreak_gauntlet/) | A defensive guardrail-evaluation harness: a categorized battery of injection/jailbreak probes scored against a guard policy (recall, false-positive rate, grade), with a decode-and-rescan defense. | red-team eval harnesses (LLM4Pentest, Secure Code Game) |
| [`prompt_evolver`](prompt_evolver/) | A genetic algorithm that evolves prompts: a prompt is a genome of instruction directives, bred across generations and selected by task accuracy. Discovers helpful directives, drops harmful ones, finds working step-orders. | DSPy / evolutionary prompt search |
| [`tiny_town`](tiny_town/) | A tiny generative-agent town: residents with traits, routines, and memories meet, converse, and form emergent friendships/rivalries over days. Each resident reuses `agent_memory`. | Stanford Generative Agents (Smallville) |
| [`agent_os`](agent_os/) | A micro agent runtime: a dependency-aware priority scheduler with parallel workers, a shared blackboard, runtime task spawning, retries, and downstream cancellation. | AutoGPT-style agent platforms |
| [`repo_cartographer`](repo_cartographer/) | Maps a Python codebase into a dependency graph via `ast` and answers impact ("what breaks if I change X"), centrality, cycles, and orphans. Maps the lab itself. | code-RAG / repo understanding |

_(more landing through the night — see [`PROGRESS.md`](PROGRESS.md))_

## Run everything

```sh
# Tour the flagship
python -m labs.agent_swarm.demo

# Run every lab's tests
python -m unittest discover -s labs -t . -p 'test_*.py'
```

## Design principles

- **Offline-first.** If it needs a key to run, it's not done. The real-model
  path is an optional enhancement behind `labs/_kernel`'s `Brain` abstraction.
- **Deterministic.** All randomness is seeded via `labs/_kernel/text.py` so
  demos and tests reproduce exactly.
- **Self-contained + shared kernel.** Each MVP owns its domain logic; the thin
  shared kernel (`_kernel/`) holds the model abstraction and text utilities.
- **Every MVP ships a README, a CLI/demo, and passing tests.**

## Shared kernel (`_kernel/`)

| Module | Purpose |
| --- | --- |
| `brain.py` | `get_brain()` → an `AnthropicBrain` when a key + SDK are present, else `None` (offline). Uniform `complete()` / `complete_json()`. |
| `text.py` | Deterministic `rng`/`stable_seed`, `keywords`, `headline`, `pick`. |
