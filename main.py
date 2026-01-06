"""
Research Agent LangGraph Demo
-----------------------
A multi-agent research workflow that:
1. Fetches news from DuckDuckGo
2. Extracts entities using GLiNER
3. Validates entities (NFL agent only)
4. Summarizes findings using Ollama LLM
5. Writes results to markdown file

Uses LangGraph for orchestration with local models.
Supports multiple agent types: NFL and Market Research.
"""

import argparse
from biz_agents import build_nfl_workflow, build_market_workflow

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

    # Print validated entities
    # print("\n\n VALIDATED ENTITIES:")
    # print("-" * 50)
    # for article_data in state.get("validated_entities", []):
    #     if article_data["entities"]:
    #         print(f"\nFrom: {article_data['article_title'][:60]}...")
    #         for entity in article_data["entities"]:
    #             label = entity["label"].upper()
    #             validated = "✓" if entity.get("validated") else "✗"
    #             print(f"  {validated} [{label}] {entity['text']}")

    print("\n\nENTITIES:")
    print("-" * 50)
    for article_data in state.get("extracted_entities", []):
        if article_data["entities"]:
            print(f"\nFrom: {article_data['article_title'][:60]}...")
            for entity in article_data["entities"]:
                label = entity["label"].upper()
                validated = "✓" if entity.get("validated") else "✗"
                print(f"  {validated} [{label}] {entity['text']}")
    
    # Print workflow messages
    print("\n\n📋 WORKFLOW LOG:")
    print("-" * 50)
    for msg in state.get("messages", []):
        print(f"  → {msg}")

    print("\n" + "=" * 70)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Multi-agent research workflow")
    parser.add_argument(
        "--agent",
        "-a",
        choices=["nfl", "market"],
        help="Agent type: 'nfl' or 'market' (will prompt if not specified)"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query for news articles (will prompt if not specified)"
    )
    args = parser.parse_args()

    # Determine agent type
    agent_type = args.agent
    if not agent_type:
        print("\nAvailable agents:")
        print("  1. nfl - NFL news research with player validation")
        print("  2. market - Market research (Knowledge Graphs, technology adoption)")
        choice = input("\nSelect agent (1 or 2): ").strip()
        agent_type = "nfl" if choice == "1" else "market"

    # Determine query
    query = args.query
    if not query:
        default_query = "NFL news today" if agent_type == "nfl" else "Knowledge Graph Adoption Today"
        query = input(f"\nEnter search query (default: '{default_query}'): ").strip()
        if not query:
            query = default_query

    print("=" * 70)
    print(f"RESEARCH LANGGRAPH DEMO - {agent_type.upper()} AGENT")
    print("=" * 70)
    print(f"Query: {query}\n")

    # Build the workflow based on agent type
    if agent_type == "nfl":
        app = build_nfl_workflow()
        initial_state = {
            "query": query,
            "news_articles": [],
            "extracted_entities": [],
            "validated_entities": [],
            "messages": []
        }
    else:
        app = build_market_workflow()
        initial_state = {
            "query": query,
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
