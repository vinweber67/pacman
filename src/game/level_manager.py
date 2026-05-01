"""Level loading and progression."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from src.entities.ghost import Ghost
from src.entities.pacman import Pacman
from src.entities.pellet import Pellet
from src.game.game_state import GameState
from src.maze.maze import Maze
from src.maze.maze_generator import MazeGenerator
from src.utils.constants import DEFAULT_LEVEL_TIME, DEFAULT_LIVES


@dataclass
class LevelData:
    """Bundle of level resources."""

    maze: Maze
    pacman: Pacman
    ghosts: list[Ghost]
    pellets: list[Pellet]


class LevelManager:
    """Load and advance levels."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.state = GameState()
        self.levels = config.get("levels", [])
        self.current_level_data: Optional[LevelData] = None

    def load_level(self, level_number: int) -> LevelData:
        """Load the requested level and update the game state."""
        index = max(0, level_number - 1)
        if index >= len(self.levels):
            self.state.is_victory = True
            raise IndexError("No more levels available")

        level_config = self.levels[index]
        width = int(level_config.get("width", 21))
        height = int(level_config.get("height", 21))
        seed = int(level_config.get("seed", 0))
        max_time = int(level_config.get("max_time", DEFAULT_LEVEL_TIME))

        maze = MazeGenerator.generate(width, height, seed)
        pacman = Pacman(width // 2, height // 2)
        ghosts = MazeGenerator.place_ghosts(maze)
        pellets = MazeGenerator.place_pellets(
            maze,
            {"pacgum_count": self.config.get("pacgum_count", 42)},
        )

        self.state.current_level = level_number
        self.state.level_time_remaining = max_time
        self.state.lives = self.state.lives or DEFAULT_LIVES
        self.state.set_maze(maze)
        self.state.set_pacman_position(pacman.x, pacman.y)
        self.state.set_ghost_positions([ghost.position for ghost in ghosts])
        self.state.set_pellet_positions(
            [
                pellet.position
                for pellet in pellets
                if not pellet.is_super
            ]
        )
        self.state.set_super_pellet_positions(
            [
                pellet.position
                for pellet in pellets
                if pellet.is_super
            ]
        )
        self.state.update_pellets(len(pellets), len(pellets))

        self.current_level_data = LevelData(
            maze=maze,
            pacman=pacman,
            ghosts=ghosts,
            pellets=pellets,
        )
        return self.current_level_data

    def advance_level(self) -> LevelData:
        """Advance to the next level."""
        next_level_number = self.state.current_level + 1
        return self.load_level(next_level_number)

    def has_more_levels(self) -> bool:
        """Return whether another level can be loaded."""
        return self.state.current_level < len(self.levels)
