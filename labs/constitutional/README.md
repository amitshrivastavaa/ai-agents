# constitutional — a self-critique & revision loop

> An agent drafts text, **critiques** it against a constitution of principles,
> **revises**, and re-critiques — looping until the draft is clean. That
> critique→revise cycle is exactly the **Constitutional AI** / **Self-Refine**
> pattern, made concrete and fully offline.

Each principle ships a rule-checkable **detector** and a deterministic **fix**,
so the loop genuinely converges to zero violations with no model. When
`ANTHROPIC_API_KEY` is set, the same loop can route critique/revision through a
real model instead.

## Quick start

```sh
python -m labs.constitutional.demo
python -m labs.constitutional.cli refine "Hey guys, this STUPID plan is GUARANTEED to always work!!!"
python -m labs.constitutional.cli refine "Reach me at a@b.com or 555-123-4567" --constitution safety
python -m labs.constitutional.cli principles
```

Example:

```
before: Hey guys, this REALLY stupid plan is GUARANTEED to always work, obviously!!!
after : Hey everyone, this unwise plan is likely to usually work, arguably!
violations per round: 9 → 0   (converged in 2 rounds)
```

## How the loop works

1. **Critique** — run every principle's detector over the draft; collect
   violations (sorted by severity).
2. **Stop** if there are none (or `max_rounds` is hit).
3. **Revise** — apply the fix of each violated principle.
4. **Re-critique** the new draft and repeat.

Because each fix is built to remove exactly what its detector flags, violations
fall monotonically to zero — you can watch the count drop each round.

## The constitution

| Principle | Rule |
| --- | --- |
| `redact_pii` (sev 5) | redact email / phone / SSN / card numbers |
| `no_insults` (sev 4) | soften insults ("stupid" → "unwise") |
| `no_overclaim` (sev 3) | drop absolutes ("guaranteed" → "likely") |
| `no_shouting` (sev 2) | de-shout ALL-CAPS (acronyms preserved) |
| `inclusive` (sev 2) | inclusive language ("guys" → "everyone", "whitelist" → "allowlist") |
| `no_exclaim` (sev 1) | collapse `!!!` / `??` |
| `no_filler` (sev 1) | cut filler ("just", "really", "basically") |

Three presets: `professional`, `safety` (PII + tone), and `all`. Add a
`Principle` (a detector + a fix) to `constitution.py` and the loop picks it up.

## Honest about rule-based revision

The fixes are deterministic find-replace, so they're predictable but blunt —
the kind of thing a real model's critique would do more gracefully. That's the
trade: this version *always runs, always converges, and never hallucinates*,
which is exactly what you want from the offline core of a critique loop.

## Tests

```sh
python -m unittest labs.constitutional.tests.test_constitutional -v
```
