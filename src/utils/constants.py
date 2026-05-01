"""Game constants and enumerations."""

from enum import Enum

# ============================================================================
# Game Constants
# ============================================================================

TILE_SIZE: int = 20  # Size of one tile in pixels
FPS: int = 60  # Target frames per second
FRAME_TIME: float = 1.0 / FPS  # Time per frame in seconds

# ============================================================================
# Screen Dimensions
# ============================================================================

DEFAULT_SCREEN_WIDTH: int = 840  # 21 tiles * 40 pixels
DEFAULT_SCREEN_HEIGHT: int = 840  # 21 tiles * 40 pixels

# ============================================================================
# Game Parameters
# ============================================================================

DEFAULT_LIVES: int = 3
DEFAULT_LEVEL_TIME: int = 90  # seconds

# ============================================================================
# Scoring
# ============================================================================

DEFAULT_POINTS_PACGUM: int = 10
DEFAULT_POINTS_SUPER_PACGUM: int = 50
DEFAULT_POINTS_GHOST: int = 200

# ============================================================================
# Colors (RGB Tuples)
# ============================================================================


class Color(Enum):
    """Color definitions for the game."""

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)  # Blinky
    PINK = (255, 184, 255)  # Pinky
    CYAN = (0, 255, 255)  # Inky
    ORANGE = (255, 184, 82)  # Clyde
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    GRAY = (128, 128, 128)
    DARK_BLUE = (0, 0, 139)


# ============================================================================
# Directions
# ============================================================================


class Direction(Enum):
    """Movement directions."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

    @property
    def dx(self) -> int:
        """Get X delta."""
        return self.value[0]

    @property
    def dy(self) -> int:
        """Get Y delta."""
        return self.value[1]

    def opposite(self) -> "Direction":
        """Get opposite direction."""
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        elif self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT
        return Direction.NONE


# ============================================================================
# Ghost Types
# ============================================================================


class GhostName(Enum):
    """Ghost identifiers."""

    BLINKY = "Blinky"
    PINKY = "Pinky"
    INKY = "Inky"
    CLYDE = "Clyde"


# ============================================================================
# Game States
# ============================================================================


class GamePhase(Enum):
    """Game phases."""

    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4
    HIGHSCORES = 5
    INSTRUCTIONS = 6
