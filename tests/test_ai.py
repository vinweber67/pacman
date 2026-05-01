"""Tests for ghost AI and pathfinding."""

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
