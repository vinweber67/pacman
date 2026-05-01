"""Tests for the highscore system."""

from __future__ import annotations

import json
from pathlib import Path

from src.highscore.highscore_manager import HighscoreManager


def test_add_score_persists_and_sorts(tmp_path: Path) -> None:
    """Scores are persisted and sorted descending."""
    filepath = tmp_path / "highscores.json"
    manager = HighscoreManager(str(filepath))

    assert manager.add_score("ALICE", 10)
    assert manager.add_score("BOB", 50)
    assert manager.add_score("CAROL", 25)

    reloaded = HighscoreManager(str(filepath))
    top = reloaded.get_top_10()

    assert [entry.name for entry in top] == ["BOB", "CAROL", "ALICE"]
    assert [entry.score for entry in top] == [50, 25, 10]
    assert all(isinstance(entry.timestamp, int) for entry in top)


def test_add_score_keeps_only_top_10(tmp_path: Path) -> None:
    """Only the top 10 entries are retained."""
    filepath = tmp_path / "highscores.json"
    manager = HighscoreManager(str(filepath))

    for i in range(10):
        assert manager.add_score(f"P{i}", 100 - i)

    assert manager.add_score("ZZ", 0) is False
    assert len(manager.get_top_10()) == 10
    assert all(entry.name != "ZZ" for entry in manager.get_top_10())


def test_invalid_names_are_rejected(tmp_path: Path) -> None:
    """Names must be <= 10 chars and alnum/spaces only."""
    filepath = tmp_path / "highscores.json"
    manager = HighscoreManager(str(filepath))

    assert manager.add_score("", 10) is False
    assert manager.add_score("this-name-is-too-long", 10) is False
    assert manager.add_score("BAD!", 10) is False


def test_negative_scores_are_clamped(tmp_path: Path) -> None:
    """Negative scores are normalized to zero."""
    filepath = tmp_path / "highscores.json"
    manager = HighscoreManager(str(filepath))

    assert manager.add_score("ALICE", -42)
    assert manager.get_top_10()[0].score == 0


def test_corrupt_file_is_handled_gracefully(tmp_path: Path) -> None:
    """Corrupt storage should not crash and should load empty list."""
    filepath = tmp_path / "highscores.json"
    filepath.write_text("{not json}", encoding="utf-8")

    manager = HighscoreManager(str(filepath))
    assert manager.get_top_10() == []


def test_invalid_entries_are_ignored(tmp_path: Path) -> None:
    """Invalid entries in JSON are skipped during load."""
    filepath = tmp_path / "highscores.json"
    filepath.write_text(
        json.dumps(
            [
                {"name": "ALICE", "score": 20, "timestamp": 1},
                {"name": "BAD!", "score": 100, "timestamp": 1},
                {"name": "BOB", "score": "30", "timestamp": 2},
                {"name": "CHARLIECHARLIE", "score": 5, "timestamp": 3},
            ]
        ),
        encoding="utf-8",
    )

    manager = HighscoreManager(str(filepath))
    top = manager.get_top_10()
    assert [entry.name for entry in top] == ["BOB", "ALICE"]
    assert [entry.score for entry in top] == [30, 20]
