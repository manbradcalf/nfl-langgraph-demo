"""Shared LangGraph nodes for research agents."""

from biz_agents.nodes.shared.nfl_news_fetcher import fetch_nfl_news
from biz_agents.nodes.shared.duckduckgo_searcher import search_duckduckgo as duckduckgo_searcher
from biz_agents.nodes.shared.entity_extractor import extract_entities
from biz_agents.nodes.shared.fact_checker import validate_entities
from biz_agents.nodes.shared.summarizer import summarize_findings
from biz_agents.nodes.shared.writer import write_research_output

__all__ = [
    "fetch_nfl_news",
    "duckduckgo_searcher",
    "extract_entities",
    "validate_entities",
    "summarize_findings",
    "write_research_output",
]
