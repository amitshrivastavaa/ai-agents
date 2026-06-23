# agent_memory — a memory that grows with you

> Give an agent a long-term memory: a stream of observations it can search by
> meaning, that gets *more useful over time* as it distills recurring themes
> into higher-level insights — and that persists across runs.

Inspired by 2026's "an agent that grows with you" wave (Hermes & friends) and
the memory architecture from Stanford's **Generative Agents** paper. Runs
**fully offline** with the standard library — embeddings are a deterministic
hashing vectorizer, reflection is keyword clustering. Set `ANTHROPIC_API_KEY`
to let a real model write the reflections instead.

## Quick start

```sh
# Narrative demo: feed a life's worth of observations, then recall + reflect
python -m labs.agent_memory.demo

# Persistent companion (state lives in ~/.agent_memory/store.json)
python -m labs.agent_memory.cli observe "Met Sara at the bouldering gym"
python -m labs.agent_memory.cli observe "Sara invited me on a climbing trip"
python -m labs.agent_memory.cli recall  "what do I do outdoors?"
python -m labs.agent_memory.cli reflect --force
python -m labs.agent_memory.cli stats
```

## The three memory systems

- **Episodic** — a time-stamped stream of observations (the "memory stream").
  Each carries an *importance* (auto-scored from emotional/biographical cue
  words, or set explicitly).
- **Semantic** — insights distilled by **reflection** once enough important
  experience has accrued. Offline, an insight names a recurring theme and cites
  the episodes behind it ("Recurring theme \"climbing\": …"); these become
  first-class memories you can also retrieve.
- **Working** — the handful of most-recent episodes: the live context window.

## Retrieval

Recall blends three signals, each min-max normalized across candidates then
weighted (the Generative-Agents scoring):

```
score = w_rel · relevance  +  w_imp · importance  +  w_rec · recency
```

- **relevance** — cosine similarity between the query embedding and the memory.
- **importance** — how much the memory mattered (1–10).
- **recency** — exponential decay since the memory was last accessed; recalling
  a memory can refresh it (`touch=True`).

Defaults lean on relevance (`1.5, 0.8, 0.8`) so query-driven search feels like
search; the paper weights them equally for autonomous *behavior*. All tunable
via `MemoryStore(weights=...)`.

## Embeddings, no dependencies

`embed()` is a **signed feature-hashing** vectorizer: every unigram and
adjacent bigram votes `±1` into a hashed bucket, then the vector is
L2-normalized. No model, no numpy — and deterministic across machines because
buckets are seeded from `hashlib`, never the salted built-in `hash()`.

## Library use

```python
from labs.agent_memory import MemoryStore

mem = MemoryStore(path="~/.agent_memory/store.json")
mem.observe("I adopted a rescue dog named Pixel", importance=8)
for hit in mem.recall("the dog", k=3):
    print(hit.score, hit.memory.text)
mem.reflect()      # distill insights when enough importance has accrued
mem.save()
```

## Tests

```sh
python -m unittest labs.agent_memory.tests.test_memory -v
```
