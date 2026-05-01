"""Pathfinding helpers for ghosts."""

from __future__ import annotations

from collections import deque
from typing import Optional

from src.maze.maze import Maze
from src.utils.types import Position


class Pathfinder:
    """Simple breadth-first pathfinding."""

    @staticmethod
    def bfs(maze: Maze, start: Position, goal: Position) -> Optional[Position]:
        """Return the next step on the shortest path to the goal."""
        if start == goal:
            return None

        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()
            for neighbor in maze.get_neighbors(*current):
                if neighbor in visited:
                    continue
                if neighbor == goal:
                    return path[1] if len(path) > 1 else neighbor
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

        return None

    @staticmethod
    def manhattan_distance(p1: Position, p2: Position) -> int:
        """Return Manhattan distance between two positions."""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
