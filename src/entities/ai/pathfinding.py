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
        path = Pathfinder.bfs_path(maze, start, goal)
        if len(path) < 2:
            return None
        return path[1]

    @staticmethod
    def bfs_path(maze: Maze, start: Position, goal: Position) -> list[Position]:
        """Return the full shortest path from start to goal if reachable."""
        if start == goal:
            return [start]

        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()
            for neighbor in maze.get_neighbors(*current):
                if neighbor in visited:
                    continue
                if neighbor == goal:
                    return path + [neighbor]
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

        return []

    @staticmethod
    def manhattan_distance(p1: Position, p2: Position) -> int:
        """Return Manhattan distance between two positions."""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
