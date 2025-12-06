"""LangGraph workflow definition."""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from nfl_agent.state import AgentState
from nfl_agent.nodes import (
    fetch_nfl_news,
    extract_entities,
    validate_entities,
    summarize_findings,
)


def build_workflow() -> CompiledStateGraph[AgentState]:
    """
    Constructs the LangGraph workflow with four nodes:
    1. fetch_news -> Fetches NFL news from DuckDuckGo
    2. extract_entities -> Extracts entities using GLiNER
    3. validate_entities -> Validates players against NFLVerse roster
    4. summarize -> Creates a summary using the LLM
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("fetch_news", fetch_nfl_news)
    workflow.add_node("extract_entities", extract_entities)
    workflow.add_node("validate_entities", validate_entities)
    workflow.add_node("summarize", summarize_findings)

    # Define edges (sequential flow)
    workflow.add_edge(START, "fetch_news")
    workflow.add_edge("fetch_news", "extract_entities")
    workflow.add_edge("extract_entities", "validate_entities")
    workflow.add_edge("validate_entities", "summarize")
    workflow.add_edge("summarize", END)

    return workflow.compile()
