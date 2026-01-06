"""LangGraph workflow definition."""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from biz_agents.nfl_agent.state import AgentState
from biz_agents.nodes.shared import (
    fetch_nfl_news,
    validate_entities,
    summarize_findings,
    write_research_output,
)
from biz_agents.nfl_agent.nodes.nfl_entity_extractor import extract_nfl_entities


def build_workflow() -> CompiledStateGraph[AgentState]:
    """
    Constructs the LangGraph workflow with five nodes:
    1. fetch_news -> Fetches NFL news from DuckDuckGo
    2. extract_entities -> Extracts entities using GLiNER
    3. validate_entities -> Validates players against NFLVerse roster
    4. summarize -> Creates a summary using the LLM
    5. write_output -> Writes research output to markdown file
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("fetch_news", fetch_nfl_news)
    workflow.add_node("extract_nfl_entities", extract_nfl_entities)
    workflow.add_node("validate_entities", validate_entities)
    workflow.add_node("summarize", summarize_findings)
    workflow.add_node("write_output", write_research_output)

    # Define edges (sequential flow)
    workflow.add_edge(START, "fetch_news")
    workflow.add_edge("fetch_news", "extract_nfl_entities")
    workflow.add_edge("extract_nfl_entities", "validate_entities")
    workflow.add_edge("validate_entities", "summarize")
    workflow.add_edge("summarize", "write_output")
    workflow.add_edge("write_output", END)

    return workflow.compile()
