"""Tile types used by the maze."""

from enum import Enum


class TileType(Enum):
    """Maze tile type."""

    WALL = 0
    CORRIDOR = 1
    SPAWN_POINT = 2
    PELLET = 3
    SUPER_PELLET = 4
