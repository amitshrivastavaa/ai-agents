# lsh — locality-sensitive hashing (approximate nearest-neighbour search)

> The trick that makes vector search — and RAG-at-scale, and every vector
> database — **sublinear** instead of `O(N)`. Random-hyperplane **SimHash** turns
> each vector into a bit signature with one magic property: two vectors at angle
> θ share a bit with probability *exactly* `1 − θ/π`. So similar vectors land in
> the same bucket and dissimilar ones don't, and a query only has to score the
> handful of vectors that share its bucket.

Companion to the lab's [`rag`](../rag/) MVP (exact TF-IDF retrieval) — this is how
you scale retrieval to millions of vectors. Offline, deterministic.

## Quick start

```sh
python -m labs.lsh.demo
python -m labs.lsh.cli search --bits 8 --tables 12
python -m labs.lsh.cli sweep
python -m labs.lsh.cli law
```

```
A query's 5 nearest neighbours (cosine similarity):
   exact (scan all):  0.87 0.87 0.86 0.86 0.85
   LSH  (scan a few): 0.87 0.87 0.86 0.86 0.85
   LSH examined 117 of 600 vectors (20%) and matched the exact top-5.
```

## How it works

- **SimHash** (`hashing.py`): each signature bit is which side of a random
  hyperplane the vector is on, `bit = 1 if v·r ≥ 0 else 0`. Geometry gives the key
  fact — a random hyperplane separates two vectors at angle θ with probability
  `θ/π`, so they **agree on a bit with probability `1 − θ/π`**. The demo and tests
  verify this empirically (e.g. cos 0.9 → 0.86 agreement, matching `1 − θ/π`).
- **Multi-table index** (`index.py`): build `L` tables, each hashing every vector
  to a `k`-bit bucket. A query gathers the union of same-bucket items across the
  `L` tables (the **candidates**) and ranks only those by exact cosine.

## The recall / speedup dial

LSH trades exactness for speed, and you steer it with two knobs:

```
   bits  tables  recall@10   scanned   speedup
      8       4        56%        6%     17.2×
      8      12        91%       14%      7.1×
     12       8        47%        3%     33.9×
```

- **More tables (`L`)** → more chances to collide → **higher recall** (more
  candidates, less speedup).
- **More bits (`k`)** → smaller buckets → **fewer candidates** (more speedup, less
  recall).

A good setting reaches **~90% recall@10 while scanning ~10–15% of the data** — a
several-× speedup that grows with `N`, since the candidate set tracks bucket
occupancy, not dataset size. That sublinearity is the whole point.

## Tests

```sh
python -m unittest labs.lsh.tests.test_lsh -v
```

9 tests: the `1 − θ/π` collision law holds empirically; signatures are
deterministic; brute force is sorted by cosine; a good config gets >85% recall@10
while scanning <30% of the data; recall rises with tables, candidates shrink with
bits; LSH's top-k overlaps the exact top-k; all deterministic.
