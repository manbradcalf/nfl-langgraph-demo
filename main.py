"""
NFL News LangGraph Demo
-----------------------
A multi-agent workflow that:
1. Fetches NFL news from DuckDuckGo
2. Extracts entities (players, teams, dates, locations, scores) using GLiNER

Uses LangGraph for orchestration with local Ollama models.
"""

from typing import TypedDict, Annotated
from operator import add

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from duckduckgo_search import DDGS
from gliner2 import GLiNER2


# =============================================================================
# State Definition
# =============================================================================

class AgentState(TypedDict):
    """State passed between agents in the graph."""
    query: str
    news_articles: list[dict]
    extracted_entities: list[dict]
    messages: Annotated[list[str], add]


# =============================================================================
# GLiNER Model (loaded once)
# =============================================================================

print("Loading GLiNER2 model...")
gliner_model = GLiNER2.from_pretrained("fastino/gliner2-base-v1")
print("GLiNER2 model loaded!\n")


# =============================================================================
# Agent 1: NFL News Fetcher
# =============================================================================

def fetch_nfl_news(state: AgentState) -> AgentState:
    """
    Fetches NFL news articles from DuckDuckGo.
    """
    query = state.get("query", "NFL news today")

    print(f"[News Fetcher] Searching for: {query}")

    with DDGS() as ddgs:
        results = list(ddgs.news(query, max_results=5))

    articles = []
    for r in results:
        articles.append({
            "title": r.get("title", ""),
            "body": r.get("body", ""),
            "source": r.get("source", ""),
            "date": r.get("date", ""),
            "url": r.get("url", "")
        })

    print(f"[News Fetcher] Found {len(articles)} articles\n")

    return {
        "news_articles": articles,
        "messages": [f"Fetched {len(articles)} NFL news articles"]
    }


# =============================================================================
# Agent 2: Entity Extractor (GLiNER)
# =============================================================================

# Entity labels for NFL context
ENTITY_LABELS = [
    "player",
    "team",
    "date",
    "location",
    "stadium",
    "score",
    "coach",
    "position"
]


def extract_entities(state: AgentState) -> AgentState:
    """
    Extracts entities from news articles using GLiNER.
    """
    articles = state.get("news_articles", [])

    print(f"[Entity Extractor] Processing {len(articles)} articles...")

    all_entities = []

    for i, article in enumerate(articles):
        # Combine title and body for extraction
        text = f"{article['title']}. {article['body']}"

        # Run GLiNER2 prediction using extract_entities
        result = gliner_model.extract_entities(text, ENTITY_LABELS)

        article_entities = {
            "article_index": i,
            "article_title": article["title"],
            "entities": []
        }

        # GLiNER2 returns {"entities": {"player": [...], "team": [...], ...}}
        entities_dict = result.get("entities", result) if isinstance(result, dict) else {}

        if isinstance(entities_dict, dict):
            for label, entity_list in entities_dict.items():
                if isinstance(entity_list, list):
                    for entity_text in entity_list:
                        if entity_text:  # Skip empty strings
                            article_entities["entities"].append({
                                "text": entity_text,
                                "label": label,
                                "score": 1.0
                            })

        all_entities.append(article_entities)
        print(f"  - Article {i+1}: Found {len(article_entities['entities'])} entities")

    total_entities = sum(len(ae["entities"]) for ae in all_entities)
    print(f"[Entity Extractor] Total entities extracted: {total_entities}\n")

    return {
        "extracted_entities": all_entities,
        "messages": [f"Extracted {total_entities} entities from {len(articles)} articles"]
    }


# =============================================================================
# Agent 3: Summarizer (uses Ollama LLM)
# =============================================================================

llm = ChatOllama(model="qwen3:8b", temperature=0)


def summarize_findings(state: AgentState) -> AgentState:
    """
    Uses the LLM to create a summary of the extracted entities.
    """
    entities = state.get("extracted_entities", [])

    # Build a summary prompt
    entity_summary = []
    for article_data in entities:
        if article_data["entities"]:
            entity_texts = [
                f"{e['label']}: {e['text']}"
                for e in article_data["entities"]
            ]
            entity_summary.append(
                f"Article: {article_data['article_title']}\n"
                f"Entities: {', '.join(entity_texts)}"
            )

    if not entity_summary:
        return {"messages": ["No entities found to summarize"]}

    prompt = f"""Based on the following NFL news entities extracted, provide a brief 2-3 sentence summary of the key information:

{chr(10).join(entity_summary)}

Summary:"""

    print("[Summarizer] Generating summary with LLM...")
    response = llm.invoke(prompt)
    summary = response.content
    print(f"[Summarizer] Done\n")

    return {"messages": [f"Summary: {summary}"]}


# =============================================================================
# Build the LangGraph Workflow
# =============================================================================

def build_workflow() -> StateGraph:
    """
    Constructs the LangGraph workflow with three nodes:
    1. fetch_news -> Fetches NFL news from DuckDuckGo
    2. extract_entities -> Extracts entities using GLiNER
    3. summarize -> Creates a summary using the LLM
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("fetch_news", fetch_nfl_news)
    workflow.add_node("extract_entities", extract_entities)
    workflow.add_node("summarize", summarize_findings)

    # Define edges (sequential flow)
    workflow.add_edge(START, "fetch_news")
    workflow.add_edge("fetch_news", "extract_entities")
    workflow.add_edge("extract_entities", "summarize")
    workflow.add_edge("summarize", END)

    return workflow.compile()


# =============================================================================
# Main Execution
# =============================================================================

def print_results(state: dict):
    """Pretty print the final results."""
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    # Print articles
    print("\n📰 NEWS ARTICLES:")
    print("-" * 50)
    for i, article in enumerate(state.get("news_articles", []), 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']} | Date: {article['date']}")
        print(f"   {article['body'][:150]}...")

    # Print entities
    print("\n\n🏈 EXTRACTED ENTITIES:")
    print("-" * 50)
    for article_data in state.get("extracted_entities", []):
        if article_data["entities"]:
            print(f"\nFrom: {article_data['article_title'][:60]}...")
            for entity in article_data["entities"]:
                print(f"  • [{entity['label'].upper()}] {entity['text']} (confidence: {entity['score']})")

    # Print workflow messages
    print("\n\n📋 WORKFLOW LOG:")
    print("-" * 50)
    for msg in state.get("messages", []):
        print(f"  → {msg}")

    print("\n" + "=" * 70)


def main():
    print("=" * 70)
    print("NFL NEWS LANGGRAPH DEMO")
    print("=" * 70)
    print()

    # Build the workflow
    app = build_workflow()

    # Initial state
    initial_state = {
        "query": "NFL football news today",
        "news_articles": [],
        "extracted_entities": [],
        "messages": []
    }

    # Run the workflow
    print("Starting workflow...\n")
    final_state = app.invoke(initial_state)

    # Display results
    print_results(final_state)


if __name__ == "__main__":
    main()
