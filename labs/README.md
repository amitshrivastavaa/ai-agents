# labs/ — a research lab of wild AI-agent MVPs

[![labs-ci](https://github.com/amitshrivastavaa/ai-agents/actions/workflows/labs-ci.yml/badge.svg)](https://github.com/amitshrivastavaa/ai-agents/actions/workflows/labs-ci.yml)

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
| [`world_model`](world_model/) | Three agents (reflex / Monte-Carlo rollout / search) plan over one gridworld model — an honest reflex→sampling→search spectrum where only full search clears every hazard maze. | world models + reasoning / planning |
| [`evo_arena`](evo_arena/) | The evolution of cooperation in the Iterated Prisoner's Dilemma: an Axelrod tournament, replicator dynamics (defection goes extinct), and a memory-1 GA where cooperation emerges or collapses by seed. | multi-agent evolution (CORAL/SAGE); Axelrod |
| [`tree_of_thoughts`](tree_of_thoughts/) | Deliberate reasoning as search on the Game of 24: beam search over partial "thoughts" scored by a Monte-Carlo value, solving 8/8 (incl. the hard 3,3,8,8) with ~2× fewer states than brute force. | test-time compute / Tree-of-Thoughts |
| [`constitutional`](constitutional/) | A self-critique & revision loop: draft → critique against a constitution of principles → revise → repeat until clean. Each principle has a rule-checkable detector + deterministic fix, so it converges offline. | Constitutional AI / Self-Refine |
| [`swarm`](swarm/) | Ant Colony Optimization for the TSP: simple ants lay pheromone and a near-optimal tour emerges (hits the optimum on solvable instances, beats greedy everywhere), drawn in ASCII. | swarm intelligence / ACO (ANTS 2026) |
| [`hopfield`](hopfield/) | Associative memory: store patterns as energy attractors and recover them from corrupted or half-erased cues. Classic Hebbian + modern dense (softmax ≈ attention); the modern net degrades far more gracefully. | Hopfield networks (Nobel 2024) |
| [`micrograd`](micrograd/) | A from-scratch reverse-mode autograd engine + a tiny MLP that genuinely learns (XOR 100%, circles, sin(x)) via backprop and SGD. Gradients verified against numerical. No numpy. | "build ML from scratch" (Karpathy micrograd) |
| [`morphogenesis`](morphogenesis/) | Gray-Scott reaction-diffusion: from a seed the field self-organizes into spots/mazes/dividing cells, and regrows after you wipe a hole — self-healing patterns in shaded ASCII. | Turing morphogenesis → Growing Neural CA |
| [`bpe`](bpe/) | A from-scratch byte-level BPE tokenizer (GPT-style): trains merges into subwords, compresses text ~2×, and round-trips *any* input exactly — emoji included. | LLM tokenization (Karpathy minbpe) |
| [`neuroevolution`](neuroevolution/) | Gradient-free RL: evolve a tiny neural-net controller to balance CartPole. Random nets last ~10 steps; the evolved one balances the full 500 and generalizes. ASCII cart view. | evolution strategies / self-improving agents |
| [`moe`](moe/) | A mixture of experts: a Gaussian-gated router sends each input to a specializing expert; trained by EM, a few experts beat a single model 14× on piecewise data, load-balanced. | Mixture-of-Experts (Jacobs 1991 → Mixtral) |
| [`symbolic_regression`](symbolic_regression/) | Genetic programming over expression trees rediscovers the *equation* behind sampled data (`x*x-2`, `x*sin(x)`, `(x*x-1)*x`) — verifier-guided evolutionary search. | evolutionary program search (AlphaEvolve) |
| [`qlearning`](qlearning/) | Tabular Q-learning learns a gridworld policy from reward alone — solves the classic cliff-walk optimally, matches value iteration; renders policy arrows + a value heatmap. | reinforcement learning (Sutton & Barto) |
| [`attention`](attention/) | Scaled dot-product attention from scratch + a hand-wired induction head that does in-context next-token prediction (`A B C A B C A → B`) with no training. | transformers / induction heads (interpretability) |

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
