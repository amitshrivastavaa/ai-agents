"""agent_swarm — a multi-agent deliberation engine.

A panel of specialist agents, each with a distinct lens and set of priorities,
argue a question over several rounds: opening statements, cross-examination,
revision under pressure, then a weighted vote a moderator synthesizes into a
decision record (verdict, confidence, consensus, dissent).

Inspired by the viral *TradingAgents* "LLM trading firm", generalized to any
high-stakes call — trades, hires, architecture choices, product bets, deals.
"""
from .engine import Deliberation, deliberate
from .personas import PANELS, Panel, Persona, get_panel

__all__ = ["Deliberation", "deliberate", "PANELS", "Panel", "Persona", "get_panel"]
