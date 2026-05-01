"""Color palette for the user interface."""

from src.utils.constants import Color

COLORS: dict[Color, tuple[int, int, int]] = {
    Color.BLACK: (0, 0, 0),
    Color.WHITE: (255, 255, 255),
    Color.RED: (255, 0, 0),
    Color.PINK: (255, 184, 255),
    Color.CYAN: (0, 255, 255),
    Color.ORANGE: (255, 184, 82),
    Color.YELLOW: (255, 255, 0),
    Color.BLUE: (0, 0, 255),
    Color.GREEN: (0, 255, 0),
    Color.GRAY: (128, 128, 128),
    Color.DARK_BLUE: (0, 0, 139),
}
