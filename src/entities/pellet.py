"""Pellet entity implementation."""

from __future__ import annotations

from src.entities.entity import Entity
from src.utils.constants import (
    DEFAULT_POINTS_PACGUM,
    DEFAULT_POINTS_SUPER_PACGUM,
)


class Pellet(Entity):
    """Collectable pellet entity."""

    def __init__(self, x: int, y: int, is_super: bool = False) -> None:
        super().__init__(x, y)
        self.is_super = is_super
        self.points = (
            DEFAULT_POINTS_SUPER_PACGUM if is_super else DEFAULT_POINTS_PACGUM
        )
        self.is_eaten = False

    def update(self, delta_time: float) -> None:
        """Pellets do not animate."""
        del delta_time

    def eat(self) -> int:
        """Mark the pellet as eaten and return its points."""
        if self.is_eaten:
            return 0
        self.is_eaten = True
        return self.points
