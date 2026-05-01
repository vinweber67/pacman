"""Collision detection helpers for core gameplay."""

from __future__ import annotations

from typing import Optional

from src.entities.ghost import Ghost
from src.entities.pacman import Pacman
from src.entities.pellet import Pellet


class CollisionDetector:
    """Utility methods for collision checks."""

    @staticmethod
    def check_pacman_ghost_collision(
        pacman: Pacman,
        ghosts: list[Ghost],
    ) -> Optional[Ghost]:
        """Return the first ghost colliding with Pacman, if any."""
        for ghost in ghosts:
            if pacman.position == ghost.position:
                return ghost
        return None

    @staticmethod
    def check_pacman_pellet_collision(
        pacman: Pacman,
        pellets: list[Pellet],
    ) -> Optional[Pellet]:
        """Return the first uneaten pellet colliding with Pacman, if any."""
        for pellet in pellets:
            if not pellet.is_eaten and pacman.position == pellet.position:
                return pellet
        return None
