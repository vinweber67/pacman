"""Tests for maze structures and generation."""

from src.entities.ghost import GhostType
from src.maze.maze import Maze
from src.maze.maze_generator import MazeGenerator
from src.maze.tile import TileType


class TestMaze:
    """Maze tests."""

    def test_creation(self) -> None:
        """Maze initializes with the right size."""
        maze = Maze(21, 21)
        assert maze.width == 21
        assert maze.height == 21

    def test_walkability(self) -> None:
        """Walls are not walkable."""
        maze = Maze(5, 5)
        assert maze.is_walkable(2, 2)
        maze.tiles[2][2] = TileType.WALL
        assert maze.is_walkable(2, 2) is False

    def test_neighbors(self) -> None:
        """Maze returns orthogonal walkable neighbors."""
        maze = Maze(5, 5)
        neighbors = maze.get_neighbors(2, 2)
        assert len(neighbors) == 4

    def test_wall_mask_blocks_movement(self) -> None:
        """Wall mask blocks adjacency even on walkable tiles."""
        maze = Maze(3, 3)
        # Block east from center and matching west on neighbor.
        maze.wall_mask[1][1] = 2
        maze.wall_mask[1][2] = 8

        assert maze.can_move(1, 1, 2, 1) is False
        neighbors = maze.get_neighbors(1, 1)
        assert (2, 1) not in neighbors


class TestMazeGenerator:
    """Maze generation tests."""

    def test_generate_creates_borders(self) -> None:
        """Generated maze has border walls."""
        maze = MazeGenerator.generate(7, 7, 42)
        assert maze.tiles[0][0] == TileType.WALL
        assert maze.tiles[6][6] == TileType.WALL

    def test_place_pellets(self) -> None:
        """Pellet placement returns pellets on walkable tiles."""
        maze = MazeGenerator.generate(7, 7, 42)
        pellets = MazeGenerator.place_pellets(maze, {"pacgum_count": 8})
        assert len(pellets) == 8
        assert any(pellet.is_super for pellet in pellets)
        assert all(maze.is_walkable(pellet.x, pellet.y) for pellet in pellets)

    def test_place_ghosts(self) -> None:
        """Ghost placement returns the four classic ghosts when possible."""
        maze = MazeGenerator.generate(7, 7, 42)
        ghosts = MazeGenerator.place_ghosts(maze)
        assert len(ghosts) == 4
        assert ghosts[0].ghost_type == GhostType.BLINKY
        assert ghosts[1].ghost_type == GhostType.PINKY
        assert ghosts[2].ghost_type == GhostType.INKY
        assert ghosts[3].ghost_type == GhostType.CLYDE
