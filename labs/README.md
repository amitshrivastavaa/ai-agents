# labs/ — a research lab of wild AI-agent MVPs

[![labs-ci](https://github.com/amitshrivastavaa/ai-agents/actions/workflows/labs-ci.yml/badge.svg)](https://github.com/amitshrivastavaa/ai-agents/actions/workflows/labs-ci.yml)

An overnight, autonomously-built collection of small but *working* MVPs, each
inspired by a trending idea in the AI-agent space. Every MVP is self-contained,
runs **offline with the Python standard library alone** (no API key, nothing to
install), and upgrades to a real model when `ANTHROPIC_API_KEY` is set.

> This directory is intentionally separate from the production `agents/` pharma
> platform — it's an experimentation sandbox. See
> [`PROGRESS.md`](PROGRESS.md) for the running build log.

## 🖼️ Showcase

- **Live gallery** → **https://amitshrivastavaa.github.io/ai-agents/** — every
  demo's real output on one page (auto-built by [`tools/build_site.py`](../tools/build_site.py)
  and published by the [`pages`](../.github/workflows/pages.yml) workflow; enable
  it once via repo *Settings → Pages → Source: GitHub Actions*).
- **Browse locally** → `python -m labs` lists all MVPs; `python -m labs <name>`
  runs one; `python -m labs --all` runs them all.
- **Rebuild the page** → `python tools/build_site.py` writes `docs/index.html`
  (open it directly — no server needed).

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
| [`rag`](rag/) | Retrieval-augmented generation from scratch: a TF-IDF index, top-k retrieval, grounded answers with citations, and abstention when the answer isn't in the knowledge base (no hallucination). | RAG (the dominant production pattern) |
| [`diffusion`](diffusion/) | A score-based diffusion generative model: annealed Langevin sampling with the analytic mixture-of-Gaussians score turns pure noise into a ring, spiral, or clusters — the real sampler, no training. | diffusion models / score-based generation |
| [`planner`](planner/) | A classical STRIPS planner: facts, actions with add/delete effects, and BFS/A* state-space search that solves the Sussman anomaly optimally. Renders block towers + the plan in ASCII. | symbolic planning / GOFAI |
| [`speculative`](speculative/) | Speculative decoding from scratch: a cheap bigram **draft** guesses k tokens, an accurate 4-gram **target** verifies a whole block per call — provably **lossless** (output identical to pure target greedy) at ~2.2× fewer target calls. | fast LLM serving (Leviathan/Chen 2023) |
| [`ssm`](ssm/) | A selective state-space model (Mamba) from scratch: the SSM **duality** (a recurrence that is exactly a convolution, to 1e-16) and **selectivity** — an input-dependent timestep solves the sample-and-hold/selective-copy task the *best possible* fixed-dynamics SSM provably cannot. The linear-time rival to attention. | state-space models / Mamba |
| [`bandits`](bandits/) | The multi-armed bandit and exploration vs exploitation: random / greedy / ε-greedy / UCB1 / Thompson scored by regret. The dumb policies stay **linear**; UCB1 and Thompson go **sublinear** (Thompson lands ~95% of pulls on the best arm). The stateless root of RL. | multi-armed bandits (UCB / Thompson) |
| [`grpo`](grpo/) | Group Relative Policy Optimization — the RL behind reasoning models (DeepSeek-R1 / RLVR) from scratch: a softmax policy trained by group-mean-baseline advantages solves a verifiable-reward task to 100%, and converges ~2.5× faster than baseline-free REINFORCE. Policy-gradient capstone of the RL thread. | reasoning-model RL (GRPO / RLVR) |
| [`flow`](flow/) | Flow matching / rectified flow from scratch — the engine of Stable Diffusion 3 & Flux. The analytic marginal velocity field `v=(ŷ−x)/(1−t)` integrates a *deterministic* ODE that flows Gaussian noise onto a ring / clusters / grid / moons / spiral in ~16 steps, full mode coverage, near-straight paths. The ODE counterpart to the `diffusion` MVP. | flow matching / rectified flow |
| [`transformer`](transformer/) | A Transformer decoder block from scratch (LayerNorm, causal multi-head attention, MLP, residual stream — verified causal and identity-when-zeroed) **and** the famous two-layer **induction circuit** (previous-token head → induction head) that does in-context learning: 100% on repeated patterns where a one-layer ablation scores 0%. Caps the from-scratch transformer thread. | transformers / induction heads |
| [`kalman`](kalman/) | The Kalman filter from scratch (with its own tiny matrix algebra incl. a Gauss-Jordan inverse): predict/update with the Kalman gain tracks a noisy 2-D object at ~40–50% lower RMSE than the raw sensor, beats a moving-average smoother, and recovers the **unmeasured velocity** — the gain settling to its optimal steady state. | Kalman filter / state estimation |
| [`lsh`](lsh/) | Locality-sensitive hashing (SimHash) for approximate nearest-neighbour search — the engine under vector DBs and RAG-at-scale. Hits **~90% recall@10 while scanning ~14% of the data** (a several-× speedup), exposes the recall/speedup dial (tables vs bits), and verifies the provable `1 − θ/π` collision law. Scales the `rag` MVP's retrieval. | vector search / ANN (SimHash) |
| [`gp`](gp/) | Gaussian Process regression from scratch (RBF kernel + Cholesky solve, closed-form, no training): curve fitting with **calibrated uncertainty** — the 95% band pinches to the noise floor at the data and balloons to the prior in gaps and extrapolation. The model knows what it doesn't know. Complements the Bayesian `kalman` filter. | Gaussian Processes / uncertainty |
| [`hmm`](hmm/) | Hidden Markov Models from scratch — log-space **Viterbi**, **forward**, and **forward-backward** — shown on the dishonest casino: recover which die (fair/loaded) was in play from the rolls alone, plus a posterior-confidence track. **Proven correct** against brute-force enumeration of every path. | HMMs / Viterbi (sequence DP) |
| [`pagerank`](pagerank/) | PageRank by power iteration — the eigenvector that ranked the web. Converges to the dominant eigenvector of the Google matrix (with teleport + dangling-node handling), and is **proven** to equal an independent random-surfer Monte-Carlo walk (agree to ~0.001). Companion to `repo_cartographer`. | PageRank / graph centrality |
| [`sketch`](sketch/) | Streaming probabilistic data structures: **Count-Min Sketch** (approximate frequencies — never underestimates, overshoot ≤ ε·N, finds heavy hitters) and **HyperLogLog** (distinct-count from max leading-zeros, ~1–3% error in ~4 KB regardless of cardinality). Fixed sublinear memory — the backbone of real-time analytics and n-gram counting at scale. | streaming sketches (CMS / HLL) |
| [`pca`](pca/) | Principal Component Analysis from scratch (power iteration + deflation, no numpy): recovers the true axes of variation exactly, components orthonormal, the optimal linear compressor — and it **discovers the true dimensionality** of low-rank data (the reconstruction-error elbow lands on the real rank). | PCA / dimensionality reduction |
| [`kmeans`](kmeans/) | k-means clustering (Lloyd's algorithm) with **k-means++** init and the **elbow** method: monotonically falling inertia, ~99% purity on separated blobs, and a clear demonstration that k-means++ crushes random init (far lower mean *and* worst-case inertia). The unsupervised companion to `pca`. | k-means / clustering |
| [`conformal`](conformal/) | Conformal prediction — distribution-free prediction intervals with a **proven ≥1−α coverage guarantee** that holds for any model and any data distribution. Empirical coverage lands exactly on 0.95/0.90/0.80 across random splits; an adaptive variant widens intervals where the noise is. The assumption-light cousin of `gp`. | conformal prediction / trustworthy ML |
| [`tree`](tree/) | A CART decision tree from scratch (Gini/entropy + greedy splits): axis-aligned cuts carve non-linear boundaries — 100% on separable blobs, ~94% on two moons (with an ASCII decision-boundary staircase), and it solves XOR a linear model can't. The depth sweep shows the overfitting gap; the building block of random forests / XGBoost. | decision trees / CART |

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
