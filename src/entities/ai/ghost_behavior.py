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
    def calculate_path(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze,
    ) -> list[Position]:
        """Return the currently intended path for a ghost."""
        if ghost.is_respawning:
            return []
        if ghost.is_edible:
            next_step = GhostAI._flee_behavior(ghost, pacman, maze)
            return GhostAI._as_path(ghost.position, next_step)
        return GhostAI._chase_path(ghost, pacman, maze)

    @staticmethod
    def calculate_next_move(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze,
    ) -> Optional[Position]:
        """Choose the next target tile for a ghost."""
        path = GhostAI.calculate_path(ghost, pacman, maze)
        if len(path) < 2:
            return None
        return path[1]

    @staticmethod
    def _chase_path(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze,
    ) -> list[Position]:
        """Return the intended chase path based on ghost archetype."""
        if ghost.ghost_type == GhostType.BLINKY:
            return GhostAI._path_towards(ghost, maze, pacman.position)

        if ghost.ghost_type == GhostType.PINKY:
            target_x = pacman.x + 4 * pacman.direction.dx
            target_y = pacman.y + 4 * pacman.direction.dy
            return GhostAI._path_towards(ghost, maze, (target_x, target_y))

        if ghost.ghost_type == GhostType.INKY:
            if random() > 0.35:
                intercept = (
                    pacman.x + 2 * pacman.direction.dx,
                    pacman.y + 2 * pacman.direction.dy,
                )
                return GhostAI._path_towards(ghost, maze, intercept)
            return GhostAI._as_path(
                ghost.position,
                GhostAI._random_move(ghost, maze),
            )

        distance = Pathfinder.manhattan_distance(
            ghost.position,
            pacman.position,
        )
        spawn_dist = Pathfinder.manhattan_distance(
            ghost.position,
            (ghost.spawn_x, ghost.spawn_y),
        )
        # Clyde flees to spawn when close to Pac-Man, but uses a hysteresis
        # dead-zone (flee < 8, only resume chase when > 12) to avoid the
        # oscillation that occurs when he sits exactly on the threshold.
        near_spawn = spawn_dist <= 3
        if distance < 8 and not near_spawn:
            return GhostAI._path_towards(
                ghost,
                maze,
                (ghost.spawn_x, ghost.spawn_y),
            )
        if distance < 12 and not near_spawn:
            # Dead zone: scatter randomly instead of bouncing between states.
            return GhostAI._as_path(
                ghost.position,
                GhostAI._random_move(ghost, maze),
            )
        return GhostAI._path_towards(ghost, maze, pacman.position)

    @staticmethod
    def _chase_behavior(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze,
    ) -> Optional[Position]:
        """Select a target based on the ghost type."""
        path = GhostAI._chase_path(ghost, pacman, maze)
        if len(path) < 2:
            return None
        return path[1]

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

    @staticmethod
    def _path_towards(
        ghost: Ghost,
        maze: Maze,
        target: Position,
    ) -> list[Position]:
        """Return a valid path toward target with safe fallbacks."""
        target_x = max(0, min(maze.width - 1, target[0]))
        target_y = max(0, min(maze.height - 1, target[1]))
        clamped_target = (target_x, target_y)

        path = Pathfinder.bfs_path(maze, ghost.position, clamped_target)
        if not path and clamped_target != target:
            path = Pathfinder.bfs_path(maze, ghost.position, target)

        if not path:
            return GhostAI._as_path(
                ghost.position,
                GhostAI._random_move(ghost, maze),
            )

        if len(path) >= 2:
            reverse = (-ghost.last_move[0], -ghost.last_move[1])
            move = (path[1][0] - ghost.x, path[1][1] - ghost.y)
            if move == reverse:
                alternatives = [
                    neighbor
                    for neighbor in maze.get_neighbors(ghost.x, ghost.y)
                    if (neighbor[0] - ghost.x, neighbor[1] - ghost.y)
                    != reverse
                ]
                if alternatives:
                    next_step = min(
                        alternatives,
                        key=lambda position: Pathfinder.manhattan_distance(
                            position,
                            clamped_target,
                        ),
                    )
                    return [ghost.position, next_step]

        return path

    @staticmethod
    def _as_path(
        start: Position,
        next_step: Optional[Position],
    ) -> list[Position]:
        """Convert a start and next step into a simple path."""
        if next_step is None:
            return []
        return [start, next_step]
