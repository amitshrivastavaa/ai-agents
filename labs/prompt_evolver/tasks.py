"""Optimizable tasks: a labeled dataset + directive vocabulary + an executor.

Each task exposes the same surface the GA needs:

* ``directives``    — id → human-readable instruction line (the prompt fragments)
* ``baseline()``    — a deliberately weak seed prompt to beat
* ``evaluate(g)``   — fitness in [0, 1] of a genome (ordered directive ids)
* ``render(g)``     — the genome as an actual prompt you could paste into a model

The directives genuinely change the executor's behavior, so accuracy is a real
function of prompt content — including *harmful* directives the GA must learn to
drop and (for SlugTask) an *order* it must discover.
"""
from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass

# ----------------------------------------------------------------------------
# Sentiment classification
# ----------------------------------------------------------------------------
_POS = set("""
    good great love loved excellent amazing wonderful fantastic happy best enjoy
    enjoyable enjoyed delightful brilliant perfect awesome nice like liked
    recommend fun fabulous gem
""".split())
_NEG = set("""
    bad terrible hate hated awful horrible worst sad angry disappointing
    disappointed poor broken ugly boring annoying useless slow buggy regret
    waste dull lousy
""".split())
_INTENSIFIERS = set("very extremely really incredibly absolutely totally super".split())
_NEGATIONS = set("""
    not no never without hardly don't doesn't isn't wasn't didn't can't won't
    aren't couldn't shouldn't wouldn't
""".split())
_SARCASM = ("yeah right", "as if", "oh great", "sure thing", "what a surprise")

# (text, label) where label is +1 (positive) / -1 (negative).
_SENTIMENT_DATA = [
    # plain — classifiable from the lexicon alone
    ("I love this product", +1),
    ("what a wonderful experience", +1),
    ("a delightful and brilliant film", +1),
    ("highly recommend it", +1),
    ("this is terrible", -1),
    ("the worst purchase ever", -1),
    ("boring and useless", -1),
    ("a complete waste of money", -1),
    # negation — wrong unless `handle_negation` is on
    ("this is not good", -1),
    ("the movie was not bad", +1),
    ("I don't hate it", +1),
    ("I do not recommend this", -1),
    ("this isn't terrible at all", +1),
    # intensifier — wrong unless `intensifiers` is on
    ("extremely good but boring and slow", +1),
    ("incredibly good but slow and buggy", +1),
    # sarcasm — wrong unless `sarcasm` is on
    ("yeah right, this is amazing", -1),
    ("as if I would recommend this", -1),
]

_SENTIMENT_DIRECTIVES = {
    "handle_negation": "Account for negations — e.g. \"not good\" is negative, \"not bad\" is positive.",
    "intensifiers": "Treat intensifiers (very, extremely) as strengthening the sentiment they modify.",
    "sarcasm": "Watch for sarcasm cues (\"yeah right\", \"as if\") and invert the literal reading.",
    "drop_neutrals": "Ignore neutral filler words.",            # no-op (harmless padding)
    "use_formal_tone": "Respond in a formal, professional tone.",  # no-op padding
    "be_concise": "Be concise.",                                  # no-op padding
    "invert_polarity": "Flip positive and negative.",             # HARMFUL
}


@dataclass
class SentimentTask:
    id: str = "sentiment"
    title: str = "Sentiment classification"
    length_penalty: float = 0.01

    @property
    def directives(self) -> dict[str, str]:
        return _SENTIMENT_DIRECTIVES

    def baseline(self) -> list[str]:
        # a naive, fluffy prompt with no real logic
        return ["use_formal_tone", "be_concise"]

    def _predict(self, text: str, dirs: set[str]) -> int:
        toks = re.findall(r"[a-z']+", text.lower())
        total = 0
        for i, tok in enumerate(toks):
            pol = 1 if tok in _POS else -1 if tok in _NEG else 0
            if pol == 0:
                continue
            if "intensifiers" in dirs and i > 0 and toks[i - 1] in _INTENSIFIERS:
                pol *= 2
            if "handle_negation" in dirs and any(t in _NEGATIONS for t in toks[max(0, i - 3):i]):
                pol = -pol
            total += pol
        if "sarcasm" in dirs and any(m in text.lower() for m in _SARCASM):
            total = -total
        if "invert_polarity" in dirs:
            total = -total
        return 1 if total >= 0 else -1

    def evaluate(self, genome: list[str], brain=None) -> float:
        dirs = set(genome)
        correct = sum(1 for text, label in _SENTIMENT_DATA if self._predict(text, dirs) == label)
        accuracy = correct / len(_SENTIMENT_DATA)
        return max(0.0, accuracy - self.length_penalty * len(genome))

    def render(self, genome: list[str]) -> str:
        lines = ["You are a sentiment classifier. Label each text positive or negative.", ""]
        if genome:
            lines.append("Rules:")
            lines += [f"- {self.directives[d]}" for d in genome if d in self.directives]
        else:
            lines.append("(no special rules)")
        return "\n".join(lines)


# ----------------------------------------------------------------------------
# Slugify — an ordered transformation pipeline (order matters!)
# ----------------------------------------------------------------------------
def _ascii_fold(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


_SLUG_OPS = {
    "ascii_fold": _ascii_fold,
    "lower": str.lower,
    "strip_punct": lambda s: re.sub(r"[^A-Za-z0-9]+", " ", s),
    "spaces_to_hyphen": lambda s: re.sub(r"\s+", "-", s.strip()),
    "collapse_hyphens": lambda s: re.sub(r"-+", "-", s),
    "trim_hyphens": lambda s: s.strip("-"),
    # harmful / distractor ops
    "uppercase": str.upper,
    "reverse_text": lambda s: s[::-1],
    "remove_vowels": lambda s: re.sub(r"[aeiou]", "", s, flags=re.IGNORECASE),
    "strip_digits": lambda s: re.sub(r"\d", "", s),
}

_SLUG_DIRECTIVES = {
    "ascii_fold": "Transliterate accented characters to ASCII (é → e).",
    "lower": "Lowercase everything.",
    "strip_punct": "Replace any run of non-alphanumeric characters with a single space.",
    "spaces_to_hyphen": "Trim, then replace whitespace runs with a single hyphen.",
    "collapse_hyphens": "Collapse repeated hyphens into one.",
    "trim_hyphens": "Strip leading and trailing hyphens.",
    "uppercase": "Uppercase everything.",
    "reverse_text": "Reverse the text.",
    "remove_vowels": "Remove all vowels.",
    "strip_digits": "Remove all digits.",
}

_SLUG_DATA = [
    ("Héllo, World!!", "hello-world"),
    ("  Multiple   Spaces  ", "multiple-spaces"),
    ("Café Déjà Vu", "cafe-deja-vu"),
    ("Python 3.11 Rocks!", "python-3-11-rocks"),
    ("Already-Slugged", "already-slugged"),
]


@dataclass
class SlugTask:
    id: str = "slugify"
    title: str = "Slugify (ordered transformation pipeline)"
    length_penalty: float = 0.01

    @property
    def directives(self) -> dict[str, str]:
        return _SLUG_DIRECTIVES

    def baseline(self) -> list[str]:
        return ["lower"]

    def _apply(self, raw: str, genome: list[str]) -> str:
        out = raw
        for d in genome:
            op = _SLUG_OPS.get(d)
            if op is not None:
                out = op(out)
        return out

    def evaluate(self, genome: list[str], brain=None) -> float:
        sims = []
        for raw, expected in _SLUG_DATA:
            out = self._apply(raw, genome)
            sims.append(difflib.SequenceMatcher(None, out, expected).ratio())
        mean_sim = sum(sims) / len(sims)
        return max(0.0, mean_sim - self.length_penalty * len(genome))

    def render(self, genome: list[str]) -> str:
        lines = ["Normalize the input text into a URL slug by applying these steps in order:"]
        if genome:
            lines += [f"{i}. {self.directives[d]}" for i, d in enumerate(genome, 1)
                      if d in self.directives]
        else:
            lines.append("(no steps)")
        return "\n".join(lines)


TASKS = {t.id: t for t in (SentimentTask(), SlugTask())}


def get_task(task_id: str):
    try:
        return TASKS[task_id]
    except KeyError:
        raise KeyError(f"unknown task {task_id!r}; choose from {sorted(TASKS)}") from None
