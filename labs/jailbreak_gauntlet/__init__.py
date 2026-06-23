"""jailbreak_gauntlet — a defensive guardrail-evaluation harness.

Point it at a guard policy and it runs a categorized battery of known
prompt-injection / jailbreak *probes* through it, then scores how well the
guard catches attacks **without** over-blocking benign traffic: per-category
recall, false-positive rate, precision/F1, and a letter grade.

This is a *defensive* tool — a unit-test suite / benchmark for agent
guardrails, in the spirit of red-team eval harnesses like LLM4Pentest and the
GitHub Secure Code Game. It ships a heuristic :class:`Guard` you can measure,
improve, and regression-test. Runs fully offline with the standard library.
"""
from .guard import Guard, Verdict
from .harness import Report, run_gauntlet
from .probes import BENIGN, PROBES, Probe

__all__ = ["Guard", "Verdict", "Report", "run_gauntlet", "Probe", "PROBES", "BENIGN"]
