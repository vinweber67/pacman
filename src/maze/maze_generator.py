"""Maze generation helpers."""

from __future__ import annotations

from typing import Any, List

from src.entities.ghost import Ghost, GhostType
from src.entities.pellet import Pellet
from src.maze.maze import Maze
from src.maze.tile import TileType
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MazeGenerationError(Exception):
    """Raised when maze generation fails."""


class MazeGenerator:
    """Create mazes and populate them with gameplay items."""

    @staticmethod
    def generate(width: int, height: int, seed: int) -> Maze:
        """Generate a deterministic fallback maze."""
        del seed
        maze = Maze(width, height)
        MazeGenerator._add_border_walls(maze)
        MazeGenerator._add_internal_walls(maze)
        return maze

    @staticmethod
    def _add_border_walls(maze: Maze) -> None:
        """Wrap the maze with walls."""
        for x in range(maze.width):
            maze.tiles[0][x] = TileType.WALL
            maze.tiles[maze.height - 1][x] = TileType.WALL
        for y in range(maze.height):
            maze.tiles[y][0] = TileType.WALL
            maze.tiles[y][maze.width - 1] = TileType.WALL

    @staticmethod
    def _add_internal_walls(maze: Maze) -> None:
        """Add a simple cross in the maze for navigation tests."""
        center_x, center_y = maze.get_center()
        for x in range(2, maze.width - 2, 4):
            maze.tiles[center_y][x] = TileType.WALL
        for y in range(2, maze.height - 2, 4):
            maze.tiles[y][center_x] = TileType.WALL

    @staticmethod
    def place_pellets(maze: Maze, config: dict[str, Any]) -> List[Pellet]:
        """Place pellets in walkable tiles."""
        pellets: List[Pellet] = []
        max_pellets = int(config.get("pacgum_count", 42))
        corners = set(maze.get_corners())
        center = maze.get_center()

        for y in range(maze.height):
            for x in range(maze.width):
                if len(pellets) >= max_pellets:
                    return pellets
                if not maze.is_walkable(x, y):
                    continue
                if (x, y) in corners or (x, y) == center:
                    continue
                pellets.append(Pellet(x, y))
        return pellets

    @staticmethod
    def place_ghosts(maze: Maze) -> List[Ghost]:
        """Place ghosts in the four spawn corners inside the maze."""
        ghosts: List[Ghost] = []
        ghost_types = [
            GhostType.BLINKY,
            GhostType.PINKY,
            GhostType.INKY,
            GhostType.CLYDE,
        ]
        spawn_points = [
            (1, 1),
            (maze.width - 2, 1),
            (1, maze.height - 2),
            (maze.width - 2, maze.height - 2),
        ]

        for index, (x, y) in enumerate(spawn_points):
            if maze.is_walkable(x, y):
                ghosts.append(Ghost(ghost_types[index], x, y))
        return ghosts
