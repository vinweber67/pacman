"""Tests for maze structures and generation."""

import pytest

from src.entities.ghost import GhostType
from src.maze.maze import Maze
from src.maze.maze_generator import MazeGenerator
from src.maze.tile import TileType
from src.utils.exceptions import MazeGenerationError


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

    def test_generate_preserves_walkable_outer_row(self) -> None:
        """Generated mazes keep the generator's outer cells playable."""
        maze = MazeGenerator.generate(7, 7, 42)
        assert maze.is_walkable(0, 0) is True
        assert maze.is_walkable(6, 6) is True

    def test_place_pellets(self) -> None:
        """Pellet placement returns pellets on walkable tiles."""
        maze = MazeGenerator.generate(7, 7, 42)
        pellets = MazeGenerator.place_pellets(maze, {"pacgum_count": 8})
        assert len(pellets) == 8
        assert any(pellet.is_super for pellet in pellets)
        assert all(maze.is_walkable(pellet.x, pellet.y) for pellet in pellets)

    def test_super_pellets_are_on_maze_corners(self) -> None:
        """Super pellets should occupy the four maze corners."""
        maze = MazeGenerator.generate(7, 7, 42)
        pellets = MazeGenerator.place_pellets(maze, {"pacgum_count": 8})

        super_positions = {
            pellet.position
            for pellet in pellets
            if pellet.is_super
        }
        assert super_positions == set(maze.get_corners())

    def test_place_ghosts(self) -> None:
        """Ghost placement returns the four classic ghosts when possible."""
        maze = MazeGenerator.generate(7, 7, 42)
        ghosts = MazeGenerator.place_ghosts(maze)
        assert len(ghosts) == 4
        assert ghosts[0].ghost_type == GhostType.BLINKY
        assert ghosts[1].ghost_type == GhostType.PINKY
        assert ghosts[2].ghost_type == GhostType.INKY
        assert ghosts[3].ghost_type == GhostType.CLYDE

    def test_ghosts_do_not_spawn_on_super_pellets(self) -> None:
        """Ghost spawns must stay distinct from power-pellet corners."""
        maze = MazeGenerator.generate(7, 7, 42)
        ghosts = MazeGenerator.place_ghosts(maze)
        pellets = MazeGenerator.place_pellets(maze, {"pacgum_count": 8})

        ghost_positions = {ghost.position for ghost in ghosts}
        super_positions = {
            pellet.position
            for pellet in pellets
            if pellet.is_super
        }

        assert ghost_positions.isdisjoint(super_positions)

    def test_generate_uses_fallback_when_wheel_fails(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Generation must not crash when wheel fails and should stay playable."""

        def fail_wheel(width: int, height: int, seed: int) -> list[list[int]]:
            raise MazeGenerationError("forced test failure")

        monkeypatch.setattr(
            MazeGenerator,
            "_generate_from_wheel",
            staticmethod(fail_wheel),
        )

        maze = MazeGenerator.generate(9, 9, 42)
        center = maze.get_center()
        assert maze.width == 9
        assert maze.height == 9
        assert maze.is_walkable(*center) is True
        assert maze.is_walkable(1, 1) is True
