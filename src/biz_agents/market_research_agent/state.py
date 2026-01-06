"""State definition for the KG Adoption news agent workflow."""

from typing import TypedDict, Annotated
from operator import add


class AgentState(TypedDict):
    """State passed between agents in the graph."""
    query: str
    news_articles: list[dict]
    extracted_entities: list[dict]
    messages: Annotated[list[str], add]
