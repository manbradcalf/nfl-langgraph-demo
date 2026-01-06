"""Summarizer node - generates summaries using Ollama LLM."""

from langchain_ollama import ChatOllama

from typing import TypedDict


llm = ChatOllama(model="qwen3:8b", temperature=0)


def summarize_findings(state: dict) -> dict:
    """
    Uses the LLM to create a summary of the validated entities.
    """
    entities = state.get("validated_entities", [])

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

    prompt = f"""Based on the following news articles extracted, provide a brief 2-3 sentence summary of the key information:

{chr(10).join(entity_summary)}

Summary:"""

    print("[Summarizer] Generating summary with LLM...")
    response = llm.invoke(prompt)
    summary = response.content
    print(f"[Summarizer] Done\n")

    return {"messages": [f"Summary: {summary}"]}
