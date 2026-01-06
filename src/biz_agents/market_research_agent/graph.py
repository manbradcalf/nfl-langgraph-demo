"""LangGraph workflow definition."""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from biz_agents.market_research_agent.state import AgentState
from biz_agents.nodes.shared import (
    duckduckgo_searcher,
    summarize_findings,
    write_research_output,
)

from biz_agents.market_research_agent.nodes.market_research_entity_extractor import extract_entities

def build_workflow() -> CompiledStateGraph[AgentState]:
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("duckduckgo_searcher", duckduckgo_searcher)
    workflow.add_node("extract_entities", extract_entities)
    workflow.add_node("summarize", summarize_findings)
    workflow.add_node("write_output", write_research_output)

    # Define edges (sequential flow)
    workflow.add_edge(START, "duckduckgo_searcher")
    workflow.add_edge("duckduckgo_searcher", "extract_entities")
    workflow.add_edge("extract_entities", "summarize")
    workflow.add_edge("summarize", "write_output")
    workflow.add_edge("write_output", END)

    return workflow.compile()
