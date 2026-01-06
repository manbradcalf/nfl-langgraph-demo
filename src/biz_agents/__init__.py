"""Biz Agents - Multi-agent research workflow package."""

from biz_agents.nfl_agent import build_workflow as build_nfl_workflow
from biz_agents.market_research_agent import build_workflow as build_market_workflow

__version__ = "0.1.0"

__all__ = [
    "build_nfl_workflow",
    "build_market_workflow",
]
