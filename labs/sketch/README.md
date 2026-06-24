# sketch — streaming probabilistic data structures (Count-Min + HyperLogLog)

> Two sketches that read a stream **once**, in **fixed memory that never grows**,
> and answer questions you couldn't afford to answer exactly: *how often does X
> appear?* and *how many distinct things are there?* They trade a sliver of
> accuracy (with provable error bounds) for unbounded scale — the backbone of
> real-time analytics and large-scale n-gram counting.

Offline, deterministic (SHA-256 hashing), with measurable error.

## Quick start

```sh
python -m labs.sketch.demo
python -m labs.sketch.cli countmin --n 200000 --width 2000
python -m labs.sketch.cli hll --n 100000 --p 12
```

```
Count-Min Sketch  (5×2000 = 10,000 counters, fixed):
         key     true  estimate  error
       login   18,276    18,306    +30      ← never underestimates
      search   18,002    18,041    +39

HyperLogLog  (4,096 registers ≈ 4 KB, fixed):
   distinct keys — true 19,926, estimated 20,565  (3.2% error)
```

## Count-Min Sketch — frequencies (`countmin.py`)

A `depth × width` grid of counters and `depth` independent hashes. Adding an item
bumps one counter per row; estimating takes the **minimum** of its counters
(collisions only ever *add*, so the min is the tightest bound).

- **Never underestimates**, and overshoots the true count by at most `ε·N`
  (`ε = e/width`) with probability `1 − e^{−depth}`.
- Memory is `O(depth·width)` — **independent of the number of distinct keys**, so
  a 10,000-counter grid tracks a 20,000-key stream (and would track 20 million the
  same way). `heavy_hitters` reads off the frequent items.

## HyperLogLog — cardinality (`hyperloglog.py`)

Hash each item to a bit-string; the **maximum number of leading zeros** seen is a
fingerprint of how many *distinct* items there were (a hash starting with `k`
zeros suggests ~`2^k` distinct items). HyperLogLog splits the stream across
`m = 2^p` registers and harmonic-means them, with a small-range linear-counting
correction.

- Relative error ~`1.04/√m` — here **~1–3% using 4,096 one-byte registers** (a few
  KB), whether the true count is thousands or billions.
- Duplicates don't inflate it (it's counting *distinct* items), and it's mergeable
  (register-wise max) — why it's everywhere in distributed analytics.

## Tests

```sh
python -m unittest labs.sketch.tests.test_sketch -v
```

11 tests: hashing is deterministic & seeded; Count-Min never underestimates and
stays within the `ε·N` bound, finds the heavy hitters (and only those), keeps an
exact total; HyperLogLog is within 7% across three orders of magnitude,
duplicates don't inflate it, empty is 0, more registers ⇒ no worse — all
deterministic.
