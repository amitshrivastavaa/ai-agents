"""Plain-English copy for the showcase — so a first-time visitor *gets it*.

The generator folds these into data.json; the frontend leads with them and keeps
each lab's technical README tagline as a secondary line. Anything missing here
falls back to the tagline, so the site still auto-grows as new labs land.
"""
from __future__ import annotations

# The landing hero — the first thing a visitor reads, so they immediately know
# what this is, why it exists, and what to do.
HERO = {
    "eyebrow": "the lab terminal",
    "headline": "How does AI actually work?",
    "body": (
        "Ever wonder what's really inside ChatGPT, AI image generators, or "
        "Google's search? This is a hands-on museum of AI & machine learning — "
        "each exhibit rebuilds one famous idea from scratch in plain Python, so "
        "you can watch the real mechanism run. No setup, no math degree."
    ),
    "cta": "Click any card to watch its demo · filter by theme · press / to search",
}

# Plain-English blurb per theme ("the six rooms").
THEME_BLURBS: dict[str, str] = {
    "agents": "Programs that act on their own — autonomous workers and characters "
              "that decide, remember, and collaborate.",
    "rl": "Learning by trial, error, and reward — like training a dog with treats. "
          "The science behind game-playing and reasoning models.",
    "evolution": "Smart behavior with no central brain — emerging from many simple "
                 "parts, or from survival of the fittest.",
    "generative": "Conjuring brand-new data out of pure noise — the family of models "
                  "behind AI image generation.",
    "transformers": "The actual guts of ChatGPT-style language models, built from "
                    "scratch.",
    "classical": "The foundational algorithms everything else stands on — from "
                 "Google's PageRank to GPS tracking to decision trees.",
}

# Plain-English description per lab. Lead with what it *is* in human terms; anchor
# to something familiar where possible.
LAB_BLURBS: dict[str, str] = {
    # — Agents —
    "agent_swarm": "A panel of AI 'experts' argue your question over a few rounds and "
                   "vote — then a moderator writes up the verdict, with its confidence "
                   "and the dissent. A boardroom in a box.",
    "agent_memory": "An AI memory that grows with you: it remembers what happened, "
                    "later finds the relevant bits by meaning (not keywords), and "
                    "slowly distills them into lasting insights. A journal that learns.",
    "agent_os": "A tiny operating system for AI tasks: it juggles many jobs at once, "
                "works out what depends on what, retries failures, and cancels work "
                "that's no longer needed. The plumbing behind AutoGPT-style agents.",
    "constitutional": "An AI that critiques and rewrites its own answer against a set "
                      "of principles, again and again, until it's clean. How models "
                      "are taught to police themselves.",
    "jailbreak_gauntlet": "A security test bench for AI guardrails: throw a battery of "
                          "sneaky 'jailbreak' attacks at a filter and score how many "
                          "it catches — and how many innocents it wrongly blocks.",
    "tiny_town": "A tiny Sims-like world: characters with personalities wake up, run "
                 "errands, bump into each other, chat, and form real friendships and "
                 "rivalries over days. Famous as Stanford's 'Smallville'.",
    "tree_of_thoughts": "Instead of blurting one answer, the AI explores a tree of "
                        "possible reasoning paths and keeps the promising ones — "
                        "solving puzzles a straight-line guess can't. Thinking as search.",
    # — Reinforcement Learning —
    "qlearning": "Learning purely from reward, with no map: an agent stumbles around a "
                 "grid, falls off cliffs, and gradually works out the best route — then "
                 "draws you the policy it learned. Reinforcement learning 101.",
    "bandits": "The gambler's dilemma, solved: with a row of slot machines, how do you "
               "balance trying new ones against milking the best one? The simplest "
               "version of every 'explore vs exploit' decision.",
    "grpo": "The reinforcement-learning trick behind reasoning models like DeepSeek-R1: "
            "let the AI try a problem many ways, reward the attempts that beat the "
            "group average, and it teaches itself to reason.",
    "world_model": "Three planners — a dumb reflex, a gambler who simulates random "
                   "futures, and a careful searcher — try to cross a hazard maze. Only "
                   "real search clears every trap. Shows what 'planning' actually buys you.",
    # — Evolution & Swarms —
    "swarm": "Simple ants wander and drop scent trails, and — with no leader and no ant "
             "seeing the whole map — a near-shortest route emerges. Nature's "
             "optimization algorithm, drawn in ASCII.",
    "evo_arena": "Does selfishness or cooperation win? Simulated strategies play the "
                 "classic 'Prisoner's Dilemma' tournament over generations — and you "
                 "watch cooperation evolve or collapse.",
    "neuroevolution": "No backprop, just survival of the fittest: breed a tiny brain "
                      "over generations until it can balance a pole on a moving cart. "
                      "Random brains last a second; the evolved one nails it.",
    "prompt_evolver": "Treats a prompt like DNA and 'breeds' better ones across "
                      "generations — discovering which instructions actually help and "
                      "which hurt. Automated prompt engineering.",
    "symbolic_regression": "Give it data and it rediscovers the actual equation behind "
                           "it (like x·sin(x)) by evolving math formulas. "
                           "Science-from-data, automated.",
    # — Generative Models —
    "diffusion": "The engine behind AI image generators (Stable Diffusion): start from "
                 "pure static and, step by step, denoise it into a clean shape — a "
                 "ring, a spiral, clusters.",
    "flow": "A newer, faster cousin of diffusion (the tech in Flux and Stable Diffusion "
            "3): it flows noise smoothly onto a target shape along a near-straight path "
            "in just a handful of steps.",
    "morphogenesis": "How a leopard gets its spots: two chemicals spreading and "
                     "reacting self-organize a blank grid into spots and mazes — and "
                     "even regrow the pattern after you punch a hole in it.",
    # — Transformers & LLM internals —
    "attention": "The single idea that makes ChatGPT work — letting each word 'look at' "
                 "the others — built from scratch, plus a hand-wired circuit that "
                 "predicts what comes next with zero training.",
    "transformer": "The full building block of a GPT, from scratch — and the famous "
                   "two-layer 'induction' circuit that lets a model pick up a pattern "
                   "on the fly, mid-sentence, without any training.",
    "bpe": "How AI reads text: it sees not letters or words but 'tokens'. This builds "
           "the tokenizer from scratch — learning to chop text into chunks and "
           "reassemble any input perfectly, emoji included.",
    "moe": "Mixture of Experts (the trick inside Mixtral and GPT-4-class models): "
           "instead of one big brain, a router sends each input to the specialist best "
           "suited to it. More capacity, less compute per token.",
    "rag": "How chatbots answer from your documents without making things up: look up "
           "the most relevant passages first, answer only from those, and say 'I don't "
           "know' when the answer isn't there.",
    "speculative": "A speed trick for language models: a cheap fast model guesses "
                   "several words ahead and the big accurate model checks them all in "
                   "one shot — identical output, ~2× faster. Used in real AI serving.",
    "ssm": "Mamba, from scratch: a rival to the Transformer that reads sequences in one "
           "efficient pass and can decide what to remember vs forget — solving a memory "
           "task plain Transformers provably can't.",
    # — Classical AI & Math —
    "pagerank": "The algorithm that built Google: rank pages by how many important "
                "pages link to them. Modeled here as a random web-surfer, proven to "
                "agree with the famous eigenvector math.",
    "kalman": "How your phone's GPS tracks you through noisy, jittery signals: blend a "
              "prediction with each messy reading to follow the true path — and even "
              "recover speed you never directly measured.",
    "hopfield": "A memory that recovers the whole from a piece: store a few patterns, "
                "then hand it a smudged or half-erased one and it snaps back to the "
                "clean original. (Won the 2024 Nobel Prize in Physics.)",
    "hmm": "Guess the hidden story behind what you see: from a string of dice rolls "
           "alone, reconstruct when a casino secretly swapped in a loaded die. The math "
           "behind speech recognition and gene-finding.",
    "gp": "A model that knows what it doesn't know: it fits a curve through your data "
          "and draws an honest uncertainty band — tight where there's data, ballooning "
          "where there isn't.",
    "lsh": "The trick that makes 'find similar items' fast at billion-scale (the engine "
           "under vector search and RAG): clever hashing finds ~90% of near-matches "
           "while looking at a tiny fraction of the data.",
    "micrograd": "Neural networks, demystified: a from-scratch engine that does the "
                 "calculus ('backprop') a real network uses to learn — small enough to "
                 "read every line, yet it genuinely learns. Karpathy's classic.",
    "planner": "Old-school AI that reasons about actions: give it blocks, a goal, and "
               "the rules, and it searches for the exact sequence of moves to get there "
               "— and draws the towers. The brains behind logistics and robots.",
    "repo_cartographer": "Maps a Python codebase like a subway map: what calls what, "
                         "what breaks if you change X, what's central, what's dead "
                         "code. Code understanding for humans (and AIs).",
    "tree": "A decision tree from scratch: ask a series of yes/no questions to sort "
            "data into outcomes — the most readable model in machine learning, and the "
            "building block of forests and boosting.",
    "forest": "A random forest: ask hundreds of slightly-different decision trees and "
              "take a vote. One tree overfits and is twitchy; the crowd is accurate and "
              "stable. A workhorse of practical ML.",
    "boosting": "Gradient boosting from scratch — the algorithm (XGBoost/LightGBM) that "
                "wins more real-world data competitions than anything else: stack many "
                "weak rules into one strong predictor, each fixing the last's mistakes.",
    "logreg": "The plain workhorse behind spam filters and credit scoring: draw the "
              "best line separating two classes by nudging it downhill toward fewer "
              "mistakes. The 'hello world' of machine learning.",
    "naivebayes": "A spam-filter classic: judge text by counting which words show up in "
                  "which category, with a dash of probability. Dead simple, "
                  "surprisingly hard to beat.",
    "kmeans": "Finds natural groups in unlabeled data: drop k flags, let each point "
              "join its nearest, move the flags to the middle, repeat — clusters "
              "emerge. Plus a trick to pick the right number of groups.",
    "pca": "Cuts the clutter from data by finding the few directions that capture most "
           "of the variation — turning a tangle of columns into a 2-D picture you can "
           "actually see. Built from scratch, no NumPy.",
    "conformal": "Turns any model's guess into an honest range with a guarantee — '95% "
                 "sure the answer is in here', and it actually holds, with no "
                 "assumptions about the data. Trust, quantified.",
    "sketch": "Answer questions about a firehose of data using almost no memory: count "
              "how often things appear, or how many unique things you've seen, in a "
              "tiny fixed space. The magic behind real-time analytics.",
}


def plain_for(name: str, fallback: str = "") -> str:
    """Plain-English description for a lab, falling back to its tagline."""
    return LAB_BLURBS.get(name, fallback)
