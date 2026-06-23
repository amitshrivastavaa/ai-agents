"""prompt_evolver — an evolutionary optimizer for prompts.

Automated prompt engineering as a genetic algorithm: a *prompt* is an ordered
set of instruction directives; the optimizer evolves a population of prompts
across generations (tournament selection, order-aware crossover, mutation,
elitism), scoring each against a labeled task, and returns the best prompt it
found plus the fitness curve.

The offline trick that makes this real without a model: each directive actually
*configures a tiny deterministic executor* for the task, so a prompt's content
changes its measured accuracy — exactly the signal a GA needs. When
``ANTHROPIC_API_KEY`` is set, a task can instead score prompts by running them
through a real model. Inspired by DSPy / evolutionary prompt search.
"""
from .evolve import Result, evolve
from .tasks import TASKS, SentimentTask, SlugTask, get_task

__all__ = ["Result", "evolve", "TASKS", "SentimentTask", "SlugTask", "get_task"]
