"""Cheat helpers for development and testing."""

from __future__ import annotations

from src.game.game_state import GameState
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CheatMode:
    """Utility cheats for evaluation and testing."""

    @staticmethod
    def toggle_invincibility(state: GameState) -> None:
        """Toggle Pac-Man invincibility."""
        new_value = not bool(getattr(state, "is_invincible", False))
        setattr(state, "is_invincible", new_value)
        logger.info("Cheat invincibility: %s", new_value)

    @staticmethod
    def skip_level(state: GameState) -> None:
        """Advance to the next level."""
        state.next_level()
        logger.info("Cheat skip level: %s", state.current_level)

    @staticmethod
    def freeze_ghosts(state: GameState) -> None:
        """Toggle ghost movement freeze."""
        new_value = not bool(getattr(state, "are_ghosts_frozen", False))
        setattr(state, "are_ghosts_frozen", new_value)
        logger.info("Cheat ghosts frozen: %s", new_value)

    @staticmethod
    def add_lives(state: GameState, count: int = 1) -> None:
        """Add extra lives to the player.

        Args:
            state: Global game state.
            count: Number of lives to add. Negative values are ignored.
        """
        if count <= 0:
            return
        state.lives += count
        logger.info("Cheat add lives: +%s (total=%s)", count, state.lives)

    @staticmethod
    def increase_speed(state: GameState, factor: float = 1.5) -> None:
        """Increase player speed multiplier.

        Args:
            state: Global game state.
            factor: Multiplier applied to current speed. Must be > 0.
        """
        if factor <= 0:
            return
        current_multiplier = float(
            getattr(state, "player_speed_multiplier", 1.0)
        )
        new_multiplier = current_multiplier * factor
        setattr(state, "player_speed_multiplier", new_multiplier)
        logger.info(
            "Cheat speed multiplier: x%s",
            new_multiplier,
        )
