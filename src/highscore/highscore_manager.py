"""Highscore management."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ScoreEntry:
    """Single score entry."""

    name: str
    score: int
    timestamp: int


class HighscoreManager:
    """Read/write score entries."""

    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)
        self.scores: List[ScoreEntry] = []
        self.load()

    def load(self) -> None:
        """Load scores from disk if possible."""
        if not self.filepath.exists():
            self.scores = []
            return

        try:
            with self.filepath.open("r", encoding="utf-8") as handle:
                raw_scores = json.load(handle)
            if not isinstance(raw_scores, list):
                logger.warning("Invalid highscores format: expected list")
                self.scores = []
                return

            loaded_scores: List[ScoreEntry] = []
            for raw_entry in raw_scores:
                parsed_entry = self._parse_entry(raw_entry)
                if parsed_entry is not None:
                    loaded_scores.append(parsed_entry)

            loaded_scores.sort(key=lambda entry: entry.score, reverse=True)
            self.scores = loaded_scores[:10]
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            logger.warning("Unable to load highscores: %s", error)
            self.scores = []

    def save(self) -> None:
        """Persist scores to disk."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with self.filepath.open("w", encoding="utf-8") as handle:
                json.dump(
                    [asdict(score) for score in self.scores],
                    handle,
                    indent=2,
                )
        except (OSError, TypeError, ValueError) as error:
            logger.error("Unable to save highscores: %s", error)

    def add_score(self, name: str, score: int) -> bool:
        """Add a score entry and keep only the top 10."""
        cleaned_name = self._normalize_name(name)
        if cleaned_name is None:
            return False

        normalized_score = max(0, int(score))
        entry = ScoreEntry(
            name=cleaned_name,
            score=normalized_score,
            timestamp=int(time.time()),
        )

        self.scores.append(entry)
        self.scores.sort(key=lambda entry: entry.score, reverse=True)
        self.scores = self.scores[:10]

        is_top_10 = any(saved_entry is entry for saved_entry in self.scores)
        if is_top_10:
            self.save()
        return is_top_10

    def get_top_10(self) -> List[ScoreEntry]:
        """Return the current top 10 scores."""
        return list(self.scores)

    def _normalize_name(self, name: str) -> str | None:
        """Validate and normalize a player name."""
        cleaned_name = name.strip()
        if not cleaned_name:
            return None
        if len(cleaned_name) > 10:
            return None
        if not all(char.isalnum() or char.isspace() for char in cleaned_name):
            return None
        return cleaned_name

    def _parse_entry(self, raw_entry: object) -> ScoreEntry | None:
        """Parse and validate one raw score entry from storage."""
        if not isinstance(raw_entry, dict):
            return None

        name_value = raw_entry.get("name")
        score_value = raw_entry.get("score")
        timestamp_value = raw_entry.get("timestamp", 0)

        if not isinstance(name_value, str):
            return None

        normalized_name = self._normalize_name(name_value)
        if normalized_name is None:
            return None

        if score_value is None:
            return None

        try:
            normalized_score = max(0, int(score_value))
            normalized_timestamp = int(timestamp_value)
        except (TypeError, ValueError):
            return None

        return ScoreEntry(
            name=normalized_name,
            score=normalized_score,
            timestamp=normalized_timestamp,
        )
