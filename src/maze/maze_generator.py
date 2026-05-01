"""Maze generation helpers."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import Any, List, cast

from src.entities.ghost import Ghost, GhostType
from src.entities.pellet import Pellet
from src.maze.maze import Maze
from src.maze.tile import TileType
from src.utils.exceptions import MazeGenerationError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
WHEEL_PATH = Path(__file__).resolve().parents[2] / "4 Pacman - data.whl"


class MazeGenerator:
    """Create mazes and populate them with gameplay items."""

    @staticmethod
    def generate(width: int, height: int, seed: int) -> Maze:
        """Generate a maze strictly from the local wheel package."""
        external_maze = MazeGenerator._generate_from_wheel(width, height, seed)
        return MazeGenerator._convert_external_maze(external_maze)

    @staticmethod
    def _generate_from_wheel(
        width: int,
        height: int,
        seed: int,
    ) -> list[list[int]]:
        """Load the wheel package dynamically and return its maze grid."""
        if not WHEEL_PATH.exists():
            raise MazeGenerationError(
                f"Required wheel not found: {WHEEL_PATH}"
            )

        try:
            wheel_path = str(WHEEL_PATH)
            if wheel_path not in sys.path:
                sys.path.insert(0, wheel_path)

            external_module = import_module("mazegenerator.mazegenerator")
            external_class = getattr(external_module, "MazeGenerator")
            generator = external_class(
                size=(width, height),
                perfect=False,
                seed=seed,
            )
            return cast(list[list[int]], generator.maze)
        except Exception as error:
            raise MazeGenerationError(
                f"Unable to load maze from wheel: {error}"
            ) from error

    @staticmethod
    def _convert_external_maze(external_maze: list[list[int]]) -> Maze:
        """Convert the wheel maze format into the gameplay Maze."""
        height = len(external_maze)
        width = len(external_maze[0]) if height > 0 else 0
        maze = Maze(width, height)

        for y, row in enumerate(external_maze):
            for x, cell in enumerate(row):
                maze.wall_mask[y][x] = int(cell)
                maze.tiles[y][x] = (
                    TileType.WALL if cell == 15 else TileType.CORRIDOR
                )

        MazeGenerator._add_border_walls(maze)
        MazeGenerator._open_spawn_points(maze)
        return maze

    @staticmethod
    def _open_spawn_points(maze: Maze) -> None:
        """Ensure the ghost spawn points remain walkable."""
        for x, y in ((1, 1), (maze.width - 2, 1), (1, maze.height - 2),
                     (maze.width - 2, maze.height - 2)):
            if 0 <= x < maze.width and 0 <= y < maze.height:
                maze.tiles[y][x] = TileType.CORRIDOR

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
    def place_pellets(maze: Maze, config: dict[str, Any]) -> List[Pellet]:
        """Place pellets in walkable tiles."""
        pellets: List[Pellet] = []
        max_pellets = int(config.get("pacgum_count", 42))
        center = maze.get_center()

        super_candidates = [
            (1, 1),
            (maze.width - 2, 1),
            (1, maze.height - 2),
            (maze.width - 2, maze.height - 2),
        ]
        super_positions: set[tuple[int, int]] = set()
        for x, y in super_candidates:
            if maze.is_walkable(x, y):
                super_positions.add((x, y))
                pellets.append(Pellet(x, y, is_super=True))

        if len(pellets) >= max_pellets:
            return pellets[:max_pellets]

        for y in range(maze.height):
            for x in range(maze.width):
                if len(pellets) >= max_pellets:
                    return pellets
                if not maze.is_walkable(x, y):
                    continue
                if (x, y) in super_positions or (x, y) == center:
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
