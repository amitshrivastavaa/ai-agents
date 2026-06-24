# evo_arena — the evolution of cooperation

> Strategies for the Iterated Prisoner's Dilemma fight it out — first in a
> classic Axelrod tournament, then under *evolution*. Watch Always-Defect go
> extinct under reciprocity, and watch cooperation **emerge from random genomes**
> in one run and **collapse to defection** in the next.

A miniature, fully-offline take on 2026's multi-agent-evolution wave (CORAL /
SAGE), built on one of the most beautiful results in game theory. Deterministic.

## Quick start

```sh
python -m labs.evo_arena.demo                       # all three acts
python -m labs.evo_arena.cli tournament             # Axelrod round-robin
python -m labs.evo_arena.cli replicator             # strategy mix evolves
python -m labs.evo_arena.cli coevolve --seed s      # cooperation EMERGES
python -m labs.evo_arena.cli coevolve --seed tragedy --rounds 80  # it COLLAPSES
```

## Three acts

**1. Axelrod tournament.** Eight classic strategies (Tit-for-Tat, Tit-for-Two-
Tats, Grim, Pavlov, Always-Cooperate, Always-Defect, Suspicious, Random) play
everyone round-robin. Nice, reciprocal strategies top the table; Always-Defect
finishes last — exactly Axelrod's 1980 finding.

**2. Replicator dynamics.** A population's *mix* of strategies shifts each
generation toward whatever scores above average. Always-Defect **goes extinct**
while reciprocators thrive: cooperation is evolutionarily stable *when
reciprocity is in the gene pool*.

```
AllD   ▂▁▁▁▁▁▁▁▁▁▁▁▁▁▁…  17% → 0%
TitForTat …               17% → 21%
```

**3. Memory-one co-evolution.** Now evolve strategies *from scratch*: a
population of memory-one genomes — `(open, p_cc, p_cd, p_dc, p_dd)`, each a
cooperation probability — co-evolves via a genetic algorithm, playing only each
other. The space contains Tit-for-Tat `(1,1,0,1,0)`, Pavlov `(1,1,0,0,1)`, and
Always-Defect `(0,0,0,0,0)`, so reciprocity can be *discovered* — or lost:

```
seed 's'       ▄▄▄▃▃▃▃▃▄▄▅▅▆▆▆  52% → 77%   cooperation EMERGES (~Grim-ish)
seed 'tragedy' ▄▄▃▂▂▂▂▁▁▁▁▁▁▁▁  51% →  2%   cooperation COLLAPSES (~AllD)
```

Same rules, different histories. In a well-mixed population defection usually
invades (the tragedy of the commons), but reciprocity can get a foothold and
take over — and a longer **shadow of the future** (`--rounds`) makes cooperation
more robust. That path-dependence *is* the lesson.

## Payoffs

Standard IPD: mutual cooperation `3/3`, defect-vs-cooperate `5/0`, mutual
defection `1/1`. `T > R > P > S` and `2R > T+S`, so cooperation is collectively
best but individually temptation beats it — the dilemma.

## Tests

```sh
python -m unittest labs.evo_arena.tests.test_arena -v
```
