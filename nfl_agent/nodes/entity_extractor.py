"""Entity extractor node - extracts entities using GLiNER."""

from gliner2 import GLiNER2

from nfl_agent.state import AgentState


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

# Load model once at module level
print("Loading GLiNER2 model...")
gliner_model = GLiNER2.from_pretrained("fastino/gliner2-base-v1")
print("GLiNER2 model loaded!\n")


def extract_entities(state: AgentState) -> dict:
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
