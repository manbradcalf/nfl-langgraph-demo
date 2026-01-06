"""NFL Fact Checker node - validates entities against NFLVerse data."""

import csv
import io
from pathlib import Path

import requests

from typing import TypedDict


class NFLFactChecker:
    """
    Validates extracted entities against NFLVerse data repositories.
    Supports multiple validation tasks that can be extended over time.

    NFLVerse data sources:
    - Rosters: https://github.com/nflverse/nflverse-data/releases/rosters
    - Schedules: https://github.com/nflverse/nflverse-data/releases/schedules
    - Player stats: https://github.com/nflverse/nflverse-data/releases/player_stats
    """

    NFLVERSE_BASE_URL = "https://github.com/nflverse/nflverse-data/releases/download"
    CACHE_DIR = Path(__file__).parent.parent.parent / ".cache" / "nflverse"

    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._roster_cache: set[str] | None = None

    def _download_csv(self, dataset: str, filename: str) -> str:
        """Downloads and caches an NFLVerse CSV file."""
        cache_path = self.CACHE_DIR / filename

        if cache_path.exists():
            print(f"[NFLFactChecker] Loading {filename} from cache...")
            return cache_path.read_text(encoding="utf-8")

        url = f"{self.NFLVERSE_BASE_URL}/{dataset}/{filename}"
        print(f"[NFLFactChecker] Downloading {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        cache_path.write_text(response.text, encoding="utf-8")
        print(f"[NFLFactChecker] Cached {filename}")
        return response.text

    def _get_roster(self, season: int = 2025) -> set[str]:
        """Loads NFL player names from NFLVerse roster data."""
        if self._roster_cache is not None:
            return self._roster_cache

        content = self._download_csv("rosters", f"roster_{season}.csv")
        reader = csv.DictReader(io.StringIO(content))

        players = set()
        for row in reader:
            # Add full_name (primary lookup)
            if full_name := row.get("full_name", "").strip():
                players.add(full_name.lower())

            # Also add "First Last" variant
            first = row.get("first_name", "").strip()
            last = row.get("last_name", "").strip()
            if first and last:
                players.add(f"{first} {last}".lower())

        print(f"[NFLFactChecker] Loaded {len(players)} player name variants")
        self._roster_cache = players
        return players

    # -------------------------------------------------------------------------
    # Validation Tasks
    # -------------------------------------------------------------------------

    def validate_player_on_roster(
        self,
        entities: list[dict],
        season: int = 2025
    ) -> list[dict]:
        """
        Validates player entities against NFLVerse roster.

        Players found in roster: label changed to 'nfl_player'
        Players not found: label changed to 'non_player' (for training data)

        Args:
            entities: List of article entity dicts from extract_entities
            season: NFL season year for roster lookup

        Returns:
            Validated entities with updated labels
        """
        roster = self._get_roster(season)

        print(f"[NFLFactChecker] Running ValidatePlayerOnRoster task...")

        validated = []
        stats = {"total": 0, "valid": 0, "invalid": 0}

        for article_data in entities:
            validated_article = {
                "article_index": article_data["article_index"],
                "article_title": article_data["article_title"],
                "entities": []
            }

            for entity in article_data["entities"]:
                new_entity = entity.copy()

                if entity["label"] == "player":
                    stats["total"] += 1
                    player_name = entity["text"].lower().strip()

                    if player_name in roster:
                        new_entity["validated"] = True
                        new_entity["label"] = "nfl_player"
                        stats["valid"] += 1
                        print(f"  ✓ '{entity['text']}' - confirmed NFL player")
                    else:
                        new_entity["validated"] = False
                        new_entity["original_label"] = "player"
                        new_entity["label"] = "non_player"
                        stats["invalid"] += 1
                        print(f"  ✗ '{entity['text']}' - NOT in NFL roster")
                else:
                    new_entity["validated"] = True

                validated_article["entities"].append(new_entity)

            validated.append(validated_article)

        print(f"\n[NFLFactChecker] Results: {stats['valid']}/{stats['total']} confirmed, "
              f"{stats['invalid']} marked non_player\n")

        return validated

    # Future validation tasks can be added here:
    # def validate_team_stats(self, ...) -> ...:
    # def validate_schedule(self, ...) -> ...:
    # def validate_player_stats(self, ...) -> ...:


# Initialize fact checker at module level
print("Initializing NFL Fact Checker...")
nfl_fact_checker = NFLFactChecker()


def validate_entities(state: dict) -> dict:
    """
    LangGraph node that runs NFLFactChecker validation tasks.
    """
    entities = state.get("extracted_entities", [])

    # Run the player roster validation task
    validated = nfl_fact_checker.validate_player_on_roster(entities)

    valid_count = sum(
        1 for a in validated for e in a["entities"]
        if e.get("label") == "nfl_player"
    )
    invalid_count = sum(
        1 for a in validated for e in a["entities"]
        if e.get("label") == "non_player"
    )

    return {
        "validated_entities": validated,
        "messages": [
            f"NFLFactChecker: {valid_count} confirmed NFL players, {invalid_count} non-players"
        ]
    }
