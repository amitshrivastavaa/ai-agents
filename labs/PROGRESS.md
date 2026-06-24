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

## Shipped to main

- PR #3 merged: MVPs #0–19 + GitHub Actions CI (`.github/workflows/labs-ci.yml`,
  runs all tests + demo smoke tests, stdlib-only) → `main`.
- PR #4 merged: #20 `qlearning` + #21 `attention` → `main`.
- PR #5 merged: #22 `rag` + #23 `diffusion` → `main`.
- PR #6 merged: #24 `planner` + #25 `speculative` → `main`.
- PR #7 merged: #26 `ssm` (Mamba) + #27 `bandits` → `main`.
- PR #8 merged: #28 `grpo` (reasoning-model RL) → `main`.
- PR #9 merged: #29 `flow` (flow matching / rectified flow) → `main`.
- PR #10 merged: #30 `transformer` (decoder block + induction circuit) → `main`.
- PR #11 merged: #31 `kalman` (Kalman filter / state estimation) → `main`.
- PR #12 merged: #32 `lsh` (locality-sensitive hashing / ANN search) → `main`.
- PR #13 merged: #33 `gp` (Gaussian Process regression) → `main`.
- PR #14 merged: #34 `hmm` (Hidden Markov Models / Viterbi) → `main`.
- PR #15 merged: #35 `pagerank` (power iteration / graph centrality) → `main`.
- PR #16 merged: #36 `sketch` (Count-Min + HyperLogLog streaming) → `main`.
- PR #17 merged: #37 `pca` (Principal Component Analysis) → `main`.
- PR #18 merged: #38 `kmeans` (k-means clustering / k-means++) → `main`.
- PR #19 merged: #39 `conformal` (distribution-free prediction intervals) → `main`.
- PR #20 merged: #40 `tree` (CART decision tree) → `main`.  ← 40 MVPs milestone
- PR #21 merged: SHOWCASE — static GitHub Pages gallery (`tools/build_site.py` →
  `docs/index.html`, `pages.yml` auto-deploy) + `python -m labs` launcher. Live at
  https://amitshrivastavaa.github.io/ai-agents/ once Pages source is set to
  "GitHub Actions" in repo settings (one-time, user must toggle).
  NOTE: regenerate `docs/index.html` (`python tools/build_site.py`) when adding an
  MVP so the committed snapshot stays current (the workflow also rebuilds on push).
- PR #22 merged: #41 `forest` (random forest, ensembles #40 tree) → `main`.
- PR #23 merged: #42 `boosting` (gradient boosting / XGBoost engine) → `main`.
The user authorized creating/merging PRs and deploying. CI is the "deploy".
Keep building on this branch; open a **follow-up PR** for each new batch (closed
PRs can't be reused) and merge it.

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

| 20 | `qlearning` | tabular Q-learning on a gridworld (cliff-walk/maze/rooms): learns the optimal policy from reward, matches value iteration; policy arrows + value heatmap | ✅ done — 9 tests green |

| 21 | `attention` | scaled dot-product attention from scratch + a hand-wired induction head doing in-context next-token prediction (no training); caps the LLM-from-scratch thread | ✅ done — 9 tests green |

| 22 | `rag` | retrieval-augmented generation from scratch: TF-IDF index + top-k retrieval + grounded extractive answers with citations + abstention (no hallucination) | ✅ done — 9 tests green |

| 23 | `diffusion` | score-based diffusion generative model from scratch: annealed Langevin sampling with the analytic GMM score turns noise into a ring/spiral/clusters (no training) | ✅ done — 7 tests green |

| 24 | `planner` | classical STRIPS planner (blocks world): BFS/A* state-space search solves the Sussman anomaly optimally; ASCII towers + plan trace (GOFAI) | ✅ done — 8 tests green |

| 25 | `speculative` | speculative decoding from scratch: a bigram draft guesses k tokens, a 4-gram target verifies a block per call — provably lossless (output == pure target greedy) at 2.2× fewer target calls (Leviathan/Chen 2023) | ✅ done — 9 tests green |

| 26 | `ssm` | selective state-space model (Mamba) from scratch: the SSM duality (recurrence ≡ convolution, to 1e-16) + selectivity — input-dependent Δ solves sample-and-hold/selective-copy that the BEST fixed-dynamics LTI provably can't (>1e9× lower MSE); pairs with attention (#21) | ✅ done — 10 tests green |

| 27 | `bandits` | multi-armed bandits: random/greedy/ε-greedy/UCB1/Thompson on a Bernoulli bandit, scored by cumulative regret — dumb policies stay linear, UCB1/Thompson go sublinear (Thompson ~95% optimal pulls); the stateless root of RL, pairs with qlearning (#20) | ✅ done — 12 tests green |

| 28 | `grpo` | Group Relative Policy Optimization from scratch (the RL behind reasoning models / DeepSeek-R1, RLVR): softmax policy + group-mean-baseline advantage solves a verifiable-reward task 100%, and converges ~2.5× faster than baseline-free REINFORCE; policy-gradient capstone of the RL thread (bandits→qlearning→grpo) | ✅ done — 9 tests green |

| 29 | `flow` | flow matching / rectified flow from scratch (the engine of Stable Diffusion 3 & Flux): analytic marginal velocity field v=(ŷ−x)/(1−t), integrate a deterministic ODE that flows N(0,I) onto ring/clusters/grid/moons/spiral in ~16 steps, 100% mode coverage, near-straight paths; pairs with diffusion (#23) | ✅ done — 10 tests green |

| 30 | `transformer` | a decoder block from scratch (LayerNorm + causal MHA + MLP + residual, verified causal/identity) AND the 2-layer induction circuit (prev-token head → induction head) that does in-context learning: 100% on repeated patterns vs 0% for a 1-layer ablation; caps bpe→micrograd→attention→transformer | ✅ done — 13 tests green |

| 31 | `kalman` | the Kalman filter from scratch (own 40-line matrix algebra incl. Gauss-Jordan inverse): predict/update with the Kalman gain tracks a noisy 2-D object at ~40-50% lower RMSE than the sensor, beats a moving-average smoother, recovers UNMEASURED velocity, gain → steady state; fills the state-estimation gap | ✅ done — 9 tests green |

| 32 | `lsh` | locality-sensitive hashing (SimHash) for approximate nearest-neighbour search — the engine under vector DBs / RAG-at-scale: ~90% recall@10 scanning ~14% of data (7× speedup), the recall/speedup dial (tables vs bits), and verifies the provable 1−θ/π collision law; pairs with rag (#22) | ✅ done — 9 tests green |

| 33 | `gp` | Gaussian Process regression from scratch (RBF kernel + Cholesky solve, no training): closed-form posterior mean+variance gives CALIBRATED uncertainty — band pinches to noise floor at data, balloons to prior in gaps/extrapolation; longer lengthscale fills gaps more confidently; complements kalman (#31) | ✅ done — 10 tests green |

| 34 | `hmm` | Hidden Markov Models from scratch (log-space Viterbi + forward + forward-backward), shown on the dishonest casino: recovers which die (fair/loaded) was in play from rolls alone (~80-95% acc) + posterior confidence; PROVEN correct vs brute-force enumeration of all paths; fills the sequence-DP gap | ✅ done — 8 tests green |

| 35 | `pagerank` | PageRank by power iteration (the eigenvector that ranked the web): converges to the dominant eigenvector of the Google matrix, handles dangling nodes + teleport; PROVEN = the random surfer's stationary distribution (Monte-Carlo cross-check matches to ~0.001); damping dial; pairs with repo_cartographer | ✅ done — 8 tests green |

| 36 | `sketch` | streaming probabilistic data structures: Count-Min Sketch (approx frequencies, never underestimates, overshoot ≤ ε·N, heavy hitters) + HyperLogLog (cardinality via max leading-zeros, ~1-3% error in 4KB regardless of count); fixed sublinear memory; the backbone of real-time analytics / n-gram counting at scale | ✅ done — 11 tests green |

| 37 | `pca` | Principal Component Analysis from scratch (power iteration + deflation, no numpy): recovers known axes exactly (PC1·true=1.000), components orthonormal, optimal linear compression; DISCOVERS true dimensionality of low-rank data (reconstruction elbow at the real rank); fills the dim-reduction gap, pairs with lsh/gp | ✅ done — 9 tests green |

| 38 | `kmeans` | k-means clustering (Lloyd) + k-means++ init + elbow method: inertia monotonically decreases, recovers separated blobs (~99% purity), k-means++ crushes random init (mean inertia 265 vs 352, far better worst-case), elbow finds true k; unsupervised companion to pca | ✅ done — 7 tests green |

| 39 | `conformal` | conformal prediction (distribution-free uncertainty, trending): split-conformal wraps any model — calibration-set residual quantile gives intervals with PROVEN ≥1−α coverage; empirical coverage lands exactly on 0.95/0.90/0.80 across 40 splits regardless of (heteroscedastic) noise; adaptive variant widens with noise; assumption-light cousin of gp | ✅ done — 7 tests green |

| 40 | `tree` | CART decision tree from scratch (Gini/entropy + greedy splits): axis-aligned cuts carve non-linear boundaries — 100% on separable blobs, ~94% on moons (ASCII decision-boundary staircase), solves XOR a linear model can't, depth sweep shows the overfitting gap; building block of RF/XGBoost. Extended with max_features for forests. | ✅ done — 9 tests green |

| 41 | `forest` | random forest from scratch (ensemble of #40's DecisionTree): bagging + √d feature subsampling decorrelate the trees; voting beats a single tree (~97.5% vs 94% on moons), variance halves with more trees, out-of-bag score ≈ test (free validation), solves XOR; caps the tree thread | ✅ done — 7 tests green |

| 42 | `boosting` | gradient boosting from scratch (the XGBoost/LightGBM engine): sequential shallow regression trees each fit the residual = negative gradient → gradient descent in function space; 150 depth-2 stumps trace sin(1.5x) (~12× better than one stump), monotone train loss, shrinkage knob; completes tree→forest→boosting | ✅ done — 8 tests green |

| 43 | `naivebayes` | multinomial Naive Bayes text classifier (counts + logs + Laplace smoothing): ~95% sentiment accuracy vs ~50% baseline, interpretable top-words per class (log-odds), smoothing handles unseen words, more data helps; fills the text-classification gap | ✅ done — 7 tests green |

(Append new ideas here as they're found. Keep the table honest.)

### Deferred / lessons
- **GAN (deferred):** attempted a from-scratch 1-D GAN for the #32 slot but hit
  the classic variance-collapse instability — a linear discriminator gives no
  variance signal, and a quadratic one drove the affine generator to a point mass
  across all seeds. Rather than ship a flaky MVP, pivoted to `lsh`. Revisit with a
  **WGAN** critic (Wasserstein + weight clipping / gradient penalty) or R1
  regularization, which are far more stable, and only ship once it passes airtight
  tests. (Airtightness > coverage.)

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
- Next wakeup: build from the unbuilt backlog. Strong next picks (all from
  scratch, offline): **multi-armed bandits** (ε-greedy / UCB1 / Thompson —
  exploration vs exploitation, regret curves), **Kalman filter** (track a noisy
  1-D/2-D object, optimal recursive estimator), **beam search vs greedy** decoding,
  **GAN** (1-D toy, generator vs discriminator), **transformer block** (attention
  #21 + residual MLP + layernorm wired into one forward pass), **n-gram LM with
  smoothing + perplexity**, **LLM-debate-for-truth** (two agents argue, judge picks).
  (#16 bpe … #25 speculative DONE.)
  Consider a fresh WebSearch round soon for newer trends.
- After each: run its tests + `unittest discover -s labs -t .`, update this table,
  commit, push.
- If you hit a usage/time limit: stop, and the loop will re-check on its
  schedule. Re-read this file when you resume.
