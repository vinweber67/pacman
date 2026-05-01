"""Tests for ghost AI and pathfinding."""

import pytest

from src.entities.ai.ghost_behavior import GhostAI
from src.entities.ai.pathfinding import Pathfinder
from src.entities.ghost import Ghost, GhostType
from src.entities.pacman import Pacman
from src.maze.maze import Maze
from src.maze.tile import TileType
from src.utils.constants import Direction


class TestPathfinder:
    """Pathfinding tests."""

    def test_manhattan_distance(self) -> None:
        """Distance uses Manhattan metric."""
        assert Pathfinder.manhattan_distance((0, 0), (3, 4)) == 7

    def test_bfs_returns_next_step(self) -> None:
        """BFS returns the first step toward the goal."""
        maze = Maze(5, 5)
        maze.tiles[2][1] = TileType.WALL
        start = (1, 1)
        goal = (3, 1)
        next_step = Pathfinder.bfs(maze, start, goal)
        assert next_step in {(1, 0), (2, 1), (1, 2)}

    def test_bfs_same_position(self) -> None:
        """No move is needed when start equals goal."""
        maze = Maze(5, 5)
        assert Pathfinder.bfs(maze, (2, 2), (2, 2)) is None


class TestGhostAI:
    """Ghost AI tests."""

    def test_blinky_chase(self) -> None:
        """Blinky chases Pac-Man directly."""
        maze = Maze(7, 7)
        pacman = Pacman(4, 4)
        pacman.direction = Direction.RIGHT
        ghost = Ghost(GhostType.BLINKY, 1, 1)
        result = GhostAI.calculate_next_move(ghost, pacman, maze)
        assert result is not None

    def test_edible_ghost_flees(self) -> None:
        """Edible ghost chooses a tile away from Pac-Man."""
        maze = Maze(7, 7)
        pacman = Pacman(3, 3)
        ghost = Ghost(GhostType.PINKY, 2, 2)
        ghost.become_edible(5.0)
        result = GhostAI.calculate_next_move(ghost, pacman, maze)
        assert result is not None
        assert result != pacman.position

    def test_clyde_random_or_chase(self) -> None:
        """Clyde returns a valid move."""
        maze = Maze(7, 7)
        pacman = Pacman(5, 5)
        ghost = Ghost(GhostType.CLYDE, 1, 1)
        result = GhostAI.calculate_next_move(ghost, pacman, maze)
        assert result is not None

    def test_pinky_targets_four_tiles_ahead(self) -> None:
        """Pinky aims toward Pac-Man projected position."""
        maze = Maze(11, 11)
        pacman = Pacman(2, 5)
        pacman.direction = Direction.RIGHT
        ghost = Ghost(GhostType.PINKY, 1, 5)

        result = GhostAI.calculate_next_move(ghost, pacman, maze)

        assert result is not None
        assert result[0] > ghost.x

    def test_inky_can_use_random_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Inky can switch to random move branch."""
        maze = Maze(7, 7)
        pacman = Pacman(3, 3)
        ghost = Ghost(GhostType.INKY, 1, 1)

        monkeypatch.setattr(
            "src.entities.ai.ghost_behavior.random",
            lambda: 0.0,
        )
        result = GhostAI.calculate_next_move(ghost, pacman, maze)
        assert result is not None

    def test_clyde_scatters_to_spawn_when_close(self) -> None:
        """When close to Pac-Man, Clyde heads back toward spawn corner."""
        maze = Maze(11, 11)
        ghost = Ghost(GhostType.CLYDE, 5, 5)
        ghost.move_to(7, 5)
        pacman = Pacman(8, 5)

        result = GhostAI.calculate_next_move(ghost, pacman, maze)

        assert result is not None
        current_dist_spawn = Pathfinder.manhattan_distance(
            ghost.position,
            (ghost.spawn_x, ghost.spawn_y),
        )
        next_dist_spawn = Pathfinder.manhattan_distance(
            result,
            (ghost.spawn_x, ghost.spawn_y),
        )
        assert next_dist_spawn <= current_dist_spawn

    def test_random_move_avoids_immediate_reverse(self) -> None:
        """Random movement avoids immediate reverse when alternatives exist."""
        maze = Maze(5, 5)
        ghost = Ghost(GhostType.INKY, 2, 2)
        ghost.last_move = (1, 0)

        for _ in range(20):
            result = GhostAI._random_move(ghost, maze)
            assert result is not None
            move = (result[0] - ghost.x, result[1] - ghost.y)
            assert move != (-1, 0)
