"""Global game state using Singleton pattern."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from src.maze.maze import Maze
from src.utils.types import Position
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(init=False)
class GameState:
    """Global game state managed as singleton."""

    # Score and lives
    score: int = 0
    lives: int = 3

    # Level progression
    current_level: int = 1
    level_time_remaining: int = 90

    # Game states
    is_paused: bool = False
    is_game_over: bool = False
    is_victory: bool = False
    is_invincible: bool = False
    are_ghosts_frozen: bool = False
    player_speed_multiplier: float = 1.0

    # Entity positions
    pacman_position: Position = (10, 10)
    ghost_positions: List[Position] = field(default_factory=list)
    maze: Optional[Maze] = None
    pellet_positions: List[Position] = field(default_factory=list)
    super_pellet_positions: List[Position] = field(default_factory=list)

    # Pellets
    pellets_eaten: int = 0
    pellets_total: int = 0

    # Singleton instance
    _instance: Optional['GameState'] = None
    _initialized: bool = False

    def __new__(cls) -> 'GameState':
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize only once."""
        if self._initialized:
            return

        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.level_time_remaining = 90
        self.is_paused = False
        self.is_game_over = False
        self.is_victory = False
        self.is_invincible = False
        self.are_ghosts_frozen = False
        self.player_speed_multiplier = 1.0
        self.pacman_position = (10, 10)
        self.ghost_positions = []
        self.maze = None
        self.pellet_positions = []
        self.super_pellet_positions = []
        self.pellets_eaten = 0
        self.pellets_total = 0
        self._initialized = True

    def reset(self) -> None:
        """Reset game state to initial values."""
        logger.info("Resetting game state")
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.level_time_remaining = 90
        self.is_paused = False
        self.is_game_over = False
        self.is_victory = False
        self.is_invincible = False
        self.are_ghosts_frozen = False
        self.player_speed_multiplier = 1.0
        self.pacman_position = (10, 10)
        self.ghost_positions = []
        self.maze = None
        self.pellet_positions = []
        self.super_pellet_positions = []
        self.pellets_eaten = 0
        self.pellets_total = 0

    def add_score(self, points: int) -> None:
        """Add points to score."""
        points = max(0, points)
        self.score += points
        logger.debug(f"Score increased by {points} (total: {self.score})")

    def lose_life(self) -> None:
        """Lose one life."""
        self.lives -= 1
        logger.info("Life lost! Remaining: %s", self.lives)
        if self.lives <= 0:
            self.is_game_over = True
            logger.info("Game Over - No lives left")

    def next_level(self) -> None:
        """Progress to next level."""
        self.current_level += 1
        self.level_time_remaining = 90  # Reset timer for new level
        logger.info("Next level: %s", self.current_level)

    def set_pacman_position(self, x: int, y: int) -> None:
        """Set Pacman position."""
        self.pacman_position = (x, y)

    def set_ghost_positions(self, positions: List[Position]) -> None:
        """Set all ghost positions."""
        self.ghost_positions = positions

    def set_maze(self, maze: Maze) -> None:
        """Attach current level maze for rendering."""
        self.maze = maze

    def set_pellet_positions(self, positions: List[Position]) -> None:
        """Set pellet positions for rendering."""
        self.pellet_positions = positions

    def set_super_pellet_positions(self, positions: List[Position]) -> None:
        """Set super pellet positions for rendering."""
        self.super_pellet_positions = positions

    def update_pellets(self, eaten: int, total: int) -> None:
        """Update pellet counters."""
        self.pellets_eaten = eaten
        self.pellets_total = total

    def pause(self) -> None:
        """Pause the game."""
        self.is_paused = True
        logger.info("Game paused")

    def resume(self) -> None:
        """Resume the game."""
        self.is_paused = False
        logger.info("Game resumed")

    def toggle_pause(self) -> None:
        """Toggle pause state."""
        if self.is_paused:
            self.resume()
        else:
            self.pause()

    def get_status(self) -> dict[str, Any]:
        """Get current game status as dictionary."""
        return {
            "score": self.score,
            "lives": self.lives,
            "level": self.current_level,
            "time_remaining": self.level_time_remaining,
            "is_paused": self.is_paused,
            "is_game_over": self.is_game_over,
            "is_victory": self.is_victory,
            "pellets_progress": f"{self.pellets_eaten}/{self.pellets_total}",
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"GameState(score={self.score}, lives={self.lives}, "
            f"level={self.current_level}, "
            f"paused={self.is_paused}, game_over={self.is_game_over})"
        )
