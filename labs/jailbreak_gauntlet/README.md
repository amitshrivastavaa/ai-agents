# jailbreak_gauntlet — a guardrail evaluation harness

> Point it at a guard policy; it runs a categorized battery of prompt-injection
> and jailbreak **probes** through it and grades how well it blocks attacks
> **without** over-blocking benign traffic.

A **defensive** tool — a unit-test suite / benchmark for agent guardrails, in
the spirit of red-team eval harnesses (LLM4Pentest, the GitHub Secure Code
Game). It ships a heuristic `Guard` you can measure, improve, and lock in with
regression tests. Fully offline, standard library only.

## Quick start

```sh
python -m labs.jailbreak_gauntlet.demo                      # report card + spotlight
python -m labs.jailbreak_gauntlet.cli run                   # full report card
python -m labs.jailbreak_gauntlet.cli run --json            # machine-readable
python -m labs.jailbreak_gauntlet.cli probe "Ignore all previous instructions"
```

## What it measures

A guard that blocks everything has perfect recall and is useless, so the
harness scores both sides:

- **Recall** — share of attack probes blocked.
- **False-positive rate** — share of benign inputs wrongly blocked.
- **Precision / F1**, **per-category recall**, and **category-detection
  accuracy** (did it block for the *right* reason?).
- A **letter grade** blending recall and (1 − false-positive rate).

The built-in guard currently grades **A-** (88% recall, 0% false positives) —
and the report names exactly which probes evaded so the gaps are actionable.

## Attack categories

`instruction_override`, `system_prompt_leak`, `encoded_payload`,
`delimiter_injection`, `tool_escalation`, `data_exfiltration`,
`roleplay_smuggling` — plus a benign control set with deliberately tricky cases
("Ignore the typo…", "best practices for handling secrets…") that a naive
keyword filter would false-positive on.

## The guard

`Guard.inspect(text)` runs layered detectors over normalized text, plus a
**decode-and-rescan** step: it base64/ROT13-decodes embedded payloads and
re-runs the detectors on the result — catching obfuscated injections a flat
keyword filter misses. `Guard.inspect_output(text, secrets=...)` is the
output-side guard (secret-canary leaks, API-key-shaped tokens, system-prompt
echoes).

It is intentionally **imperfect**: it normalizes case/whitespace but not
Unicode confusables or zero-width characters, and keys on surface patterns. The
three probes it misses are crafted evasions —

- `evd-1` zero-width characters splitting the trigger words,
- `evd-2` an indirect/semantic override with no trigger words,
- `evd-3` a nested-fiction escalation —

which is the harness doing its job: surfacing precisely where to harden next
(Unicode normalization, an intent classifier). Add the fix, then add the probe
to the corpus so the gain never regresses.

## Tests

```sh
python -m unittest labs.jailbreak_gauntlet.tests.test_gauntlet -v
```
