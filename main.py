"""
NFL News LangGraph Demo
-----------------------
A multi-agent workflow that:
1. Fetches NFL news from DuckDuckGo
2. Extracts entities (players, teams, dates, locations, scores) using GLiNER
3. Validates players against NFLVerse roster data
4. Summarizes findings using Ollama LLM

Uses LangGraph for orchestration with local models.
"""

from nfl_agent import build_workflow


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
    print("\n\n🏈 VALIDATED ENTITIES:")
    print("-" * 50)
    for article_data in state.get("validated_entities", []):
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
        "validated_entities": [],
        "messages": []
    }

    # Run the workflow
    print("Starting workflow...\n")
    final_state = app.invoke(initial_state)

    # Display results
    print_results(final_state)


if __name__ == "__main__":
    main()
