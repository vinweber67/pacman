"""Ghost AI behaviors."""

from __future__ import annotations

from random import choice, random
from typing import Optional

from src.entities.ai.pathfinding import Pathfinder
from src.entities.ghost import Ghost, GhostType
from src.entities.pacman import Pacman
from src.maze.maze import Maze
from src.utils.types import Position


class GhostAI:
    """Behavior helpers for ghosts."""

    @staticmethod
    def calculate_next_move(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze,
    ) -> Optional[Position]:
        """Choose the next target tile for a ghost."""
        if ghost.is_respawning:
            return None
        if ghost.is_edible:
            return GhostAI._flee_behavior(ghost, pacman, maze)
        return GhostAI._chase_behavior(ghost, pacman, maze)

    @staticmethod
    def _chase_behavior(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze,
    ) -> Optional[Position]:
        """Select a target based on the ghost type."""
        if ghost.ghost_type == GhostType.BLINKY:
            return Pathfinder.bfs(maze, ghost.position, pacman.position)

        if ghost.ghost_type == GhostType.PINKY:
            target_x = pacman.x + 4 * pacman.direction.dx
            target_y = pacman.y + 4 * pacman.direction.dy
            return Pathfinder.bfs(maze, ghost.position, (target_x, target_y))

        if ghost.ghost_type == GhostType.INKY:
            if random() > 0.5:
                return Pathfinder.bfs(maze, ghost.position, pacman.position)
            return GhostAI._random_move(ghost, maze)

        distance = Pathfinder.manhattan_distance(
            ghost.position,
            pacman.position,
        )
        if distance < 8:
            return GhostAI._random_move(ghost, maze)
        return Pathfinder.bfs(maze, ghost.position, pacman.position)

    @staticmethod
    def _flee_behavior(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze,
    ) -> Optional[Position]:
        """Move away from Pac-Man."""
        neighbors = maze.get_neighbors(ghost.x, ghost.y)
        if not neighbors:
            return None
        return max(
            neighbors,
            key=lambda position: Pathfinder.manhattan_distance(
                position,
                pacman.position,
            ),
        )

    @staticmethod
    def _random_move(ghost: Ghost, maze: Maze) -> Optional[Position]:
        """Return a random walkable neighbor."""
        neighbors = maze.get_neighbors(ghost.x, ghost.y)
        if not neighbors:
            return None
        return choice(neighbors)
