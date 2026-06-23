# tiny_town — a tiny generative-agent town

> Five townspeople with personalities, daily routines, and memories live in a
> small world. They follow their schedules, run into each other, hold short
> conversations, and — over a few days — form friendships and quiet rivalries.
> Nobody scripts the relationships; they **emerge**.

A miniature, fully-offline homage to Stanford's *Generative Agents*
("Smallville"). Each resident's memory is an
[`agent_memory`](../agent_memory/) store, so the town doubles as a demo of the
lab's pieces composing. Deterministic via the shared seeded RNG.

## Quick start

```sh
python -m labs.tiny_town.demo                    # 3 days: snapshot + chronicle + summary
python -m labs.tiny_town.cli --days 3            # chronicle + summary
python -m labs.tiny_town.cli --days 2 --watch    # also print the who's-where board each phase
python -m labs.tiny_town.cli --days 3 --json     # relationships + metadata
```

## The residents

| Who | Traits | Home / Work |
| --- | --- | --- |
| Alice | outgoing, foodie | Home_A / Office |
| Cleo | athletic, outgoing | Home_A / Office |
| Bram | bookish, quiet | Home_B / Library |
| Dex | foodie, quiet | Home_B / Market |
| Wren | bookish, athletic | Home_C / Library |

## How a day unfolds

Each day has six phases (morning → night). At each phase every resident heads to
a location chosen by their **routine and traits**: home to sleep, work in the
forenoon, the Cafe or Market at noon, the Park or Library in the afternoon, a
social spot in the evening. When two residents share a location they **converse**
about a topic drawn from their shared traits and where they are, each records a
**memory**, and their **relationship** eases toward their underlying
*affinity* (shared traits attract; strangers stay cool) plus a little "we met
again" warmth. At day's end each resident **reflects** on who they keep running
into.

What emerges:

- The Cafe fills up at noon (Alice, Cleo, Dex) — a natural recurring meetup.
- Alice & Cleo share a home, an office, and the cafe → they rack up meetings and
  become the town's strongest bond.
- Cleo & Dex share no traits and keep chatting "stiffly" → they drift into a
  cool acquaintance.
- Reflections surface the social truth: *"Recurring theme: cleo"* — Alice
  realizes Cleo is everywhere in her life.

Run more days and the top bond only strengthens — relationships compound, just
like the memory that feeds them.

## Pieces

- `world.py` — the map, locations, and the roster of residents.
- `sim.py` — routines, encounters, affinity, conversation, reflection.
- `render.py` — the who's-where board, the chronicle, the summary.

## Tests

```sh
python -m unittest labs.tiny_town.tests.test_town -v
```
