"""Maze generation helpers."""

from __future__ import annotations

import random
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

    _external_class: Any = None

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

            if MazeGenerator._external_class is None:
                external_module = import_module("mazegenerator.mazegenerator")
                MazeGenerator._external_class = getattr(
                    external_module,
                    "MazeGenerator",
                )

            return MazeGenerator._fast_generate_external_maze(
                MazeGenerator._external_class,
                width,
                height,
                seed,
            )
        except Exception as error:
            raise MazeGenerationError(
                f"Unable to load maze from wheel: {error}"
            ) from error

    @staticmethod
    def _fast_generate_external_maze(
        external_class: Any,
        width: int,
        height: int,
        seed: int,
    ) -> list[list[int]]:
        """Generate maze while skipping expensive shortest-path computation.

        The assigned package computes shortest path in constructor.
        That path is not required for gameplay and can add latency.
        This adapter path keeps package methods untouched.
        It falls back to the constructor path if the internal API differs.
        """
        try:
            generator = external_class.__new__(external_class)
            generator._width = width
            generator._height = height
            generator._perfect = False
            generator._seed = seed
            generator._entryx = 0
            generator._entryy = 0
            generator._exitx = width - 1
            generator._exity = height - 1
            generator._maze = []
            generator._path = []
            generator._shortest_path = False

            random.seed(seed) if seed > 0 else random.seed()
            generator._create_empty_maze()
            generator._add_42_to_maze()
            generator._generate_maze(generator._entryx, generator._entryy, 0)
            return cast(list[list[int]], generator.maze)
        except Exception:
            fallback = external_class(
                size=(width, height),
                perfect=False,
                seed=seed,
            )
            return cast(list[list[int]], fallback.maze)

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
        seed = int(config.get("seed", 0))
        rng = random.Random(seed)
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

        candidates: list[tuple[int, int]] = []
        for y in range(maze.height):
            for x in range(maze.width):
                if not maze.is_walkable(x, y):
                    continue
                if (x, y) in super_positions or (x, y) == center:
                    continue
                candidates.append((x, y))

        remaining = max_pellets - len(pellets)
        if remaining <= 0 or not candidates:
            return pellets

        if remaining >= len(candidates):
            for x, y in candidates:
                pellets.append(Pellet(x, y))
            return pellets

        rng.shuffle(candidates)
        selected: list[tuple[int, int]] = [candidates[0]]
        selected_set = {candidates[0]}

        while len(selected) < remaining:
            best_pos: tuple[int, int] | None = None
            best_distance = -1
            for candidate in candidates:
                if candidate in selected_set:
                    continue
                distance = min(
                    abs(candidate[0] - sx) + abs(candidate[1] - sy)
                    for sx, sy in selected
                )
                if distance > best_distance:
                    best_distance = distance
                    best_pos = candidate
            if best_pos is None:
                break
            selected.append(best_pos)
            selected_set.add(best_pos)

        for x, y in selected:
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
