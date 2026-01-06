"""Writer node - saves research output to markdown files."""

import os
from datetime import datetime
from pathlib import Path

def write_research_output(state: dict) -> dict:
    """
    Writes the research query, summary, and other relevant information
    to a markdown file in the research_output directory.
    """
    # Create research_output directory if it doesn't exist
    output_dir = Path("research_output")
    output_dir.mkdir(exist_ok=True)

    # Generate filename based on timestamp and query
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    query = state.get("query", "unknown_query")
    # Sanitize query for filename (replace spaces and special chars)
    safe_query = "".join(c if c.isalnum() else "_" for c in query)[:50]
    filename = f"{timestamp}_{safe_query}.md"
    filepath = output_dir / filename

    # Extract data from state
    query = state.get("query", "No query specified")
    news_articles = state.get("news_articles", [])
    validated_entities = state.get("validated_entities", [])
    extracted_entities = state.get("extracted_entities",[])
    messages = state.get("messages", [])

    # Find the summary from messages
    summary = "No summary available"
    for msg in messages:
        if msg.startswith("Summary:"):
            summary = msg.replace("Summary:", "").strip()
            break

    # Build markdown content
    markdown_content = f"""# Research Report

## Query
{query}

## Summary
{summary}

## Research Date
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## News Articles ({len(news_articles)} found)
"""

    # Add news articles
    for i, article in enumerate(news_articles, 1):
        title = article.get("title", "No title")
        url = article.get("url", "")
        snippet = article.get("body", "No content available")

        markdown_content += f"""
### {i}. {title}
- **URL**: {url}
- **Content**: {snippet}
"""

    # Add validated entities
    markdown_content += f"""
## Extracted Entities
"""

    if validated_entities:
        for article_data in validated_entities:
            article_title = article_data.get("article_title", "Unknown article")
            entities = article_data.get("entities", [])

            if entities:
                markdown_content += f"""
### From: {article_title}
"""
                for entity in entities:
                    label = entity.get("label", "Unknown")
                    text = entity.get("text", "")
                    markdown_content += f"- **{label}**: {text}\n"
    # If we don't have validated entities, display extracted entities with unvalidated caveat
    elif extracted_entities:
        for article_data in extracted_entities:
            article_title = article_data.get("article_title", "Unknown article")
            entities = article_data.get("entities", [])

            if entities:
                markdown_content += f"""
### From: {article_title}
"""
                for entity in entities:
                    label = entity.get("label", "Unknown")
                    text = entity.get("text", "")
                    markdown_content += f"- **{label}**: {text}\n"
    else:
        markdown_content += "\nNo entities extracted.\n"

    # Write to file
    print(f"[Writer] Writing research output to {filepath}...")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"[Writer] Successfully saved to {filepath}")

    return {"messages": [f"Research output saved to {filepath}"]}
