"""morphogenesis — self-organizing, self-healing patterns from local rules.

A Gray-Scott reaction-diffusion system: two virtual chemicals diffuse and react
on a grid, and from a tiny seed the whole field organizes itself into spots,
stripes, mazes, or dividing "cells" — Turing's morphogenesis, the same lineage
as Growing Neural Cellular Automata. Cut a hole in a formed pattern and it grows
back: the dynamics are self-healing.

Fully offline, deterministic, fast enough in pure Python, and rendered as
shaded ASCII you can watch evolve.
"""
from .grid import Grid, PRESETS, get_preset
from .render import shade

__all__ = ["Grid", "PRESETS", "get_preset", "shade"]
