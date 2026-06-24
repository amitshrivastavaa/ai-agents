"""Scripted demo: feed a life's worth of observations, then recall and reflect.

    python -m labs.agent_memory.demo

Uses a throwaway in-memory store (no file written), fully offline.
"""
from __future__ import annotations

from .memory import MemoryStore

DIARY = [
    "I started a new job as a backend engineer at a climate-tech startup.",
    "Met Sara at the bouldering gym; she's training for an outdoor climbing trip.",
    "Spent Saturday hiking Eagle Ridge — I love being out on the trail.",
    "Standup was rough; the orders service had an outage and I was on call.",
    "Sara invited me to a weekend climbing trip in the Sierras. Nervous but excited.",
    "Fixed the flaky deploy pipeline that's been haunting the team for months.",
    "Cooked dinner for Mom's birthday; she cried, it was a good night.",
    "Long run along the river before work — trail running is becoming my thing.",
    "Got promoted to senior engineer. First time I've felt truly recognized.",
    "Climbing trip with Sara was incredible — terrified on the crux but sent it.",
]

QUERIES = [
    "what do I do for fun outdoors?",
    "tell me about Sara",
    "how is work going?",
]


def main() -> int:
    store = MemoryStore(dims=256, reflect_threshold=25.0)

    print("Feeding the memory stream …\n")
    for line in DIARY:
        m = store.observe(line)
        print(f"  +#{m.id} (imp {m.importance:.0f}) {line}")
        new = store.reflect()
        for ins in new:
            print(f"      ✦ reflection: {ins.text}")

    print("\n— Working set (live context window) —")
    for m in store.working_set(5):
        print(f"  · {m.text}")

    for q in QUERIES:
        print(f"\n— Recall: {q!r} —")
        for rank, h in enumerate(store.recall(q, k=3), 1):
            tag = "✦" if h.memory.kind == "semantic" else "·"
            print(f"  {rank}. [{h.score:4.2f}] {tag} {h.memory.text}")

    st = store.stats()
    print(f"\nstats: {st['total']} memories "
          f"({st['episodic']} episodic, {st['semantic']} semantic) over {st['tick']} ticks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
