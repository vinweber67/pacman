"""Pac-Man entity implementation."""

from __future__ import annotations

from src.entities.entity import Entity
from src.utils.constants import Direction


class Pacman(Entity):
    """Pac-Man player entity."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.direction: Direction = Direction.NONE
        self.next_direction: Direction = Direction.NONE
        self.is_invincible: bool = False

    def update(self, delta_time: float) -> None:
        """Update the player state."""
        del delta_time
        if self.next_direction != Direction.NONE:
            self.direction = self.next_direction
            self.next_direction = Direction.NONE

    def set_direction(self, direction: Direction) -> None:
        """Queue a direction change."""
        self.next_direction = direction

    def move(self, dx: int, dy: int) -> None:
        """Move the player by a delta."""
        self.x += dx
        self.y += dy
