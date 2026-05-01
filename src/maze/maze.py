"""Maze representation for the gameplay layer."""

from __future__ import annotations

from typing import List

from src.maze.tile import TileType
from src.utils.types import Position


class Maze:
    """Grid-based maze representation."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles: List[List[TileType]] = [
            [TileType.CORRIDOR for _ in range(width)]
            for _ in range(height)
        ]
        self.wall_mask: List[List[int]] = [
            [0 for _ in range(width)]
            for _ in range(height)
        ]

    def is_walkable(self, x: int, y: int) -> bool:
        """Return whether a tile can be walked on."""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return self.tiles[y][x] != TileType.WALL

    @staticmethod
    def _direction_to_mask(dx: int, dy: int) -> tuple[int, int]:
        """Convert a movement delta into wall bitmasks.

        Returns:
            Tuple of (current_cell_wall_bit, neighbor_cell_opposite_wall_bit)
        """
        if dx == 0 and dy == -1:  # north
            return 1, 4
        if dx == 1 and dy == 0:  # east
            return 2, 8
        if dx == 0 and dy == 1:  # south
            return 4, 1
        if dx == -1 and dy == 0:  # west
            return 8, 2
        return 0, 0

    def can_move(self, x: int, y: int, next_x: int, next_y: int) -> bool:
        """Return whether movement between two adjacent tiles is possible."""
        if not self.is_walkable(x, y) or not self.is_walkable(next_x, next_y):
            return False

        dx = next_x - x
        dy = next_y - y
        if abs(dx) + abs(dy) != 1:
            return False

        current_bit, opposite_bit = self._direction_to_mask(dx, dy)
        if current_bit == 0:
            return False

        if len(self.wall_mask) != self.height:
            return True
        if not all(len(row) == self.width for row in self.wall_mask):
            return True

        current_mask = self.wall_mask[y][x]
        next_mask = self.wall_mask[next_y][next_x]
        return (
            (current_mask & current_bit) == 0
            and (next_mask & opposite_bit) == 0
        )

    def get_neighbors(self, x: int, y: int) -> List[Position]:
        """Return walkable orthogonal neighbors."""
        neighbors: List[Position] = []
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            next_x = x + dx
            next_y = y + dy
            if self.can_move(x, y, next_x, next_y):
                neighbors.append((next_x, next_y))
        return neighbors

    def get_center(self) -> Position:
        """Return the maze center."""
        return (self.width // 2, self.height // 2)

    def get_corners(self) -> list[Position]:
        """Return maze corners."""
        return [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
        ]
