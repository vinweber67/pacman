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

    def is_walkable(self, x: int, y: int) -> bool:
        """Return whether a tile can be walked on."""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return self.tiles[y][x] != TileType.WALL

    def get_neighbors(self, x: int, y: int) -> List[Position]:
        """Return walkable orthogonal neighbors."""
        neighbors: List[Position] = []
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            next_x = x + dx
            next_y = y + dy
            if self.is_walkable(next_x, next_y):
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
