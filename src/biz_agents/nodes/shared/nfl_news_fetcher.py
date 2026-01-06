"""News fetcher node - fetches NFL news from DuckDuckGo."""

from duckduckgo_search import DDGS

from typing import TypedDict


def fetch_nfl_news(state: dict) -> dict:
    """
    Fetches news articles from DuckDuckGo.
    """
    query = state.get("query") 

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
