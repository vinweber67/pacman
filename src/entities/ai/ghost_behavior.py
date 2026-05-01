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
            return GhostAI._next_step_towards(
                ghost,
                maze,
                pacman.position,
            )

        if ghost.ghost_type == GhostType.PINKY:
            target_x = pacman.x + 4 * pacman.direction.dx
            target_y = pacman.y + 4 * pacman.direction.dy
            return GhostAI._next_step_towards(
                ghost,
                maze,
                (target_x, target_y),
            )

        if ghost.ghost_type == GhostType.INKY:
            # Inky: unpredictable mix between intercept and random motion.
            if random() > 0.35:
                intercept = (
                    pacman.x + 2 * pacman.direction.dx,
                    pacman.y + 2 * pacman.direction.dy,
                )
                return GhostAI._next_step_towards(ghost, maze, intercept)
            return GhostAI._random_move(ghost, maze)

        # Clyde: chase when far, scatter back to home corner when close.
        distance = Pathfinder.manhattan_distance(
            ghost.position,
            pacman.position,
        )
        if distance < 8:
            return GhostAI._next_step_towards(
                ghost,
                maze,
                (ghost.spawn_x, ghost.spawn_y),
            )
        return GhostAI._next_step_towards(ghost, maze, pacman.position)

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
        reverse = (-ghost.last_move[0], -ghost.last_move[1])
        filtered = [
            neighbor
            for neighbor in neighbors
            if (neighbor[0] - ghost.x, neighbor[1] - ghost.y) != reverse
        ]
        options = filtered or neighbors
        return max(
            options,
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
        reverse = (-ghost.last_move[0], -ghost.last_move[1])
        filtered = [
            neighbor
            for neighbor in neighbors
            if (neighbor[0] - ghost.x, neighbor[1] - ghost.y) != reverse
        ]
        return choice(filtered or neighbors)

    @staticmethod
    def _next_step_towards(
        ghost: Ghost,
        maze: Maze,
        target: Position,
    ) -> Optional[Position]:
        """Return a valid step toward target with safe fallbacks."""
        target_x = max(0, min(maze.width - 1, target[0]))
        target_y = max(0, min(maze.height - 1, target[1]))
        clamped_target = (target_x, target_y)

        next_step = Pathfinder.bfs(maze, ghost.position, clamped_target)
        if next_step is None and clamped_target != target:
            next_step = Pathfinder.bfs(maze, ghost.position, target)

        if next_step is None:
            return GhostAI._random_move(ghost, maze)

        reverse = (-ghost.last_move[0], -ghost.last_move[1])
        move = (next_step[0] - ghost.x, next_step[1] - ghost.y)
        if move == reverse:
            alternatives = [
                neighbor
                for neighbor in maze.get_neighbors(ghost.x, ghost.y)
                if (neighbor[0] - ghost.x, neighbor[1] - ghost.y) != reverse
            ]
            if alternatives:
                return min(
                    alternatives,
                    key=lambda position: Pathfinder.manhattan_distance(
                        position,
                        clamped_target,
                    ),
                )

        return next_step
