"""hmm — Hidden Markov Models with Viterbi and forward-backward, from scratch.

A Markov chain over hidden states you can't see, each emitting an observation you
can. Three exact dynamic-programming algorithms (all in log space):

* **Viterbi** — the single most likely hidden path,
* **forward** — the total probability of the observations,
* **forward-backward** — the per-position posterior over states.

Demonstrated on the canonical **dishonest casino** (recover when a dealer swapped
in a loaded die), and *proved* correct against brute-force enumeration of every
path. Offline, deterministic.
"""
from .model import HMM, logsumexp
from .casino import casino_hmm, sample, accuracy
from . import brute

__all__ = ["HMM", "logsumexp", "casino_hmm", "sample", "accuracy", "brute"]
