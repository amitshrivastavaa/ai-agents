"""Theme assignment for the labs showcase.

Each lab gets one *primary* theme (editorial — easily tweaked). ``THEMES`` holds
the display label and a subtle accent tint layered over the phosphor-green base.
"""
from __future__ import annotations

# theme id -> display label + accent colour (hex), layered over phosphor green.
THEMES: dict[str, dict[str, str]] = {
    "agents":       {"label": "Agents",                       "accent": "#3ad6ff"},
    "rl":           {"label": "Reinforcement Learning",       "accent": "#ffb454"},
    "evolution":    {"label": "Evolution & Swarms",           "accent": "#a6ff5f"},
    "generative":   {"label": "Generative Models",            "accent": "#ff6fd0"},
    "transformers": {"label": "Transformers & LLM internals", "accent": "#b39dff"},
    "classical":    {"label": "Classical AI & Math",          "accent": "#5fffd0"},
}

# lab directory name -> theme id. Keep in sync with the labs that ship a demo.py;
# test_build.py::test_theme_map_matches_discovered_labs guards both directions.
THEME_MAP: dict[str, str] = {
    "agent_memory": "agents",
    "agent_os": "agents",
    "agent_swarm": "agents",
    "constitutional": "agents",
    "jailbreak_gauntlet": "agents",
    "tiny_town": "agents",
    "tree_of_thoughts": "agents",
    "bandits": "rl",
    "grpo": "rl",
    "qlearning": "rl",
    "world_model": "rl",
    "evo_arena": "evolution",
    "neuroevolution": "evolution",
    "prompt_evolver": "evolution",
    "swarm": "evolution",
    "symbolic_regression": "evolution",
    "diffusion": "generative",
    "flow": "generative",
    "morphogenesis": "generative",
    "attention": "transformers",
    "bpe": "transformers",
    "moe": "transformers",
    "rag": "transformers",
    "speculative": "transformers",
    "ssm": "transformers",
    "transformer": "transformers",
    "gp": "classical",
    "hmm": "classical",
    "hopfield": "classical",
    "kalman": "classical",
    "lsh": "classical",
    "micrograd": "classical",
    "pagerank": "classical",
    "planner": "classical",
    "repo_cartographer": "classical",
}


def theme_for(name: str) -> str:
    """Theme id for a lab; unmapped labs fall back to 'classical' so the build
    never crashes (a CI test nudges you to assign new labs explicitly)."""
    return THEME_MAP.get(name, "classical")
