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
| 7 | `repo_cartographer` | map a Python repo into a dependency/knowledge graph (AST) + answer "what depends on X" | ✅ done — 12 tests green, maps the lab itself |
| 8 | `world_model` | "think before you act" planners (reflex/rollout/search) over a gridworld model — honest reflex→sampling→search spectrum | ✅ done — 10 tests green |
| 9 | `evo_arena` | co-evolving IPD strategies (Axelrod tournament + replicator dynamics + memory-1 GA) — cooperation emerges or collapses (CORAL/SAGE evolution) | ✅ done — 12 tests green |

| 10 | `tree_of_thoughts` | deliberate reasoning search on Game of 24 — beam over "thoughts" w/ Monte-Carlo value, vs random/brute; test-time compute | ✅ done — 10 tests green, solves 8/8 incl. (3,3,8,8) |
| 11 | `constitutional` | self-critique & revision loop: draft → critique vs a constitution → revise until clean (Constitutional AI / Self-Refine) | ✅ done — 11 tests green |
| 12 | `swarm` | Ant Colony Optimization for TSP — pheromone trails, emergent shortest tour (swarm intelligence; ANTS 2026) | ✅ done — 9 tests green, hits optimal on circle/random8, ASCII tour plots |
| 13 | `hopfield` | associative memory: store patterns, recover from corrupted/partial input (energy-based attractors; Nobel 2024) | ✅ done — 10 tests green, classic + modern, ASCII recall |

| 14 | `micrograd` | a from-scratch reverse-mode autograd engine + a tiny MLP that learns (XOR/circles/sine) via backprop & SGD — "build ML from scratch" | ✅ done — 11 tests green, gradients verified vs numerical |

| 15 | `morphogenesis` | Gray-Scott reaction-diffusion: self-organizing + self-healing Turing patterns (morphogenesis → Growing Neural CA), shaded ASCII | ✅ done — 7 tests green, regrows after damage |

| 16 | `bpe` | a from-scratch byte-level BPE tokenizer (GPT-style): train merges, encode/decode with exact round-trip, compression scales w/ vocab | ✅ done — 12 tests green |

| 17 | `neuroevolution` | gradient-free RL: evolve a tiny neural-net controller to balance CartPole (random ~10 steps → evolved 500, generalizes), ASCII cart | ✅ done — 9 tests green |

| 18 | `moe` | mixture of experts: Gaussian-gated router + EM-specialized linear experts beat a single model 14× on piecewise data; load-balanced (Mixtral lineage) | ✅ done — 10 tests green |

| 19 | `symbolic_regression` | genetic programming over expression trees rediscovers formulas from data (x*x-2, x*sin(x), x³-x) — verifier-guided evolutionary search (AlphaEvolve) | ✅ done — 11 tests green |

(Append new ideas here as they're found. Keep the table honest.)

### Idea sources (second research round, June 2026)
- Test-time compute / **Tree-of-Thoughts** reasoning is THE theme (o1-style "think
  before answering"). → `tree_of_thoughts` (#10).
- **Constitutional AI / self-critique** loops (Critique Fine-Tuning, +15% on hard
  tasks). → `constitutional` (#11).
- **Swarm intelligence / ACO** (ANTS 2026, Darmstadt, June 8-10). → `swarm` (#12).
- **Hopfield / dense associative memory** (Nobel 2024, renewed interest). →
  `hopfield` (#13).
- AlphaEvolve (evolutionary search + a verifier "clock") & Agent0 (adversarial
  co-evolution) — partly covered by prompt_evolver/evo_arena; revisit later.

### Idea sources (June 2026 research)
- Multi-agent **evolution** is hot: CORAL (autonomous multi-agent evolution on
  open-ended problems, persistent memory, 3-10x over fixed baselines), SAGE &
  Group-Evolving Agents (co-evolving agents, experience sharing, 71% SWE-bench).
  → `evo_arena` (#9).
- **World models + reasoning** (o3/R1/extended-thinking → single-call planning,
  DeerFlow long-horizon agents). → `world_model` (#8).
- Memory as a first-class primitive (Ontheia/pgvector) — already covered by
  `agent_memory`. Graph orchestration (LangGraph) — covered by `agent_os`.

## How to run what exists

```sh
python -m labs.agent_swarm.demo                 # tour
python -m labs.agent_swarm.cli --list           # panels
python -m unittest discover -s labs -t . -p 'test_*.py'   # all lab tests
```

## Next steps (for the next wakeup)

- #10-15 (tree_of_thoughts, constitutional, swarm, hopfield, micrograd,
  morphogenesis) DONE.
- Next wakeup: build from the unbuilt backlog. Strong next picks: BPE tokenizer
  (from scratch, foundational, fast), MoE router (gating + experts + load
  balancing), PDDL/STRIPS planner (symbolic AI), AlphaEvolve-style symbolic
  regression (evolve a formula, verified). Then a fresh WebSearch round.
  Unbuilt backlog: diffusion-from-scratch, speculative decoding,
  LLM-debate-for-truth, PDDL/STRIPS planner, RAG/vector-search from scratch,
  q-learning gridworld, transformer-attention-from-scratch.
  (#16 bpe, #17 neuroevolution, #18 moe, #19 symbolic_regression DONE.)
  Consider a fresh WebSearch round soon for newer trends.
- After each: run its tests + `unittest discover -s labs -t .`, update this table,
  commit, push.
- If you hit a usage/time limit: stop, and the loop will re-check on its
  schedule. Re-read this file when you resume.
