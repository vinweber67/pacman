"""Ghost entity implementation."""

from __future__ import annotations

from enum import Enum

from src.entities.entity import Entity
from src.utils.constants import Color, GhostName


class GhostType(Enum):
    """Ghost types used by the gameplay layer."""

    BLINKY = GhostName.BLINKY.value
    PINKY = GhostName.PINKY.value
    INKY = GhostName.INKY.value
    CLYDE = GhostName.CLYDE.value


class Ghost(Entity):
    """Ghost entity with edible state."""

    def __init__(self, ghost_type: GhostType, x: int, y: int) -> None:
        super().__init__(x, y)
        self.ghost_type = ghost_type
        self.color = self._ghost_color(ghost_type)
        self.is_edible: bool = False
        self.edible_timer: float = 0.0
        self.is_respawning: bool = False
        self.respawn_timer: float = 0.0
        self.spawn_x: int = x
        self.spawn_y: int = y
        self.last_move: tuple[int, int] = (0, 0)

    @staticmethod
    def _ghost_color(ghost_type: GhostType) -> Color:
        """Return the color associated with a ghost."""
        if ghost_type == GhostType.BLINKY:
            return Color.RED
        if ghost_type == GhostType.PINKY:
            return Color.PINK
        if ghost_type == GhostType.INKY:
            return Color.CYAN
        return Color.ORANGE

    def update(self, delta_time: float) -> None:
        """Update the ghost state."""
        if self.is_respawning:
            self.respawn_timer = max(0.0, self.respawn_timer - delta_time)
            if self.respawn_timer == 0.0:
                self.respawn()
            return

        if self.is_edible:
            self.edible_timer = max(0.0, self.edible_timer - delta_time)
            if self.edible_timer == 0.0:
                self.is_edible = False

    def move_to(self, x: int, y: int) -> None:
        """Move the ghost and keep track of last movement vector."""
        self.last_move = (x - self.x, y - self.y)
        super().move_to(x, y)

    def become_edible(self, duration: float) -> None:
        """Make the ghost edible for a duration."""
        self.is_edible = True
        self.edible_timer = max(0.0, duration)

    def respawn(self) -> None:
        """Return the ghost to its spawn point."""
        self.move_to(self.spawn_x, self.spawn_y)
        self.is_respawning = False
        self.respawn_timer = 0.0
        self.is_edible = False
        self.edible_timer = 0.0
        self.last_move = (0, 0)

    def start_respawn(self, delay: float) -> None:
        """Hide the ghost then respawn it after a delay."""
        self.is_respawning = True
        self.respawn_timer = max(0.0, delay)
        self.is_edible = False
        self.edible_timer = 0.0
        self.move_to(-1, -1)
        self.last_move = (0, 0)
