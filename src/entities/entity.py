"""Base entity class for the game."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.utils.types import Position


@dataclass
class Entity(ABC):
    """Base class for all entities."""

    x: int
    y: int

    @property
    def position(self) -> Position:
        """Return the entity position as a tuple."""
        return (self.x, self.y)

    def move_to(self, x: int, y: int) -> None:
        """Move the entity to a new position."""
        self.x = x
        self.y = y

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update the entity state."""
        raise NotImplementedError
