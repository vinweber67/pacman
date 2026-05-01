"""Tests for utilities."""

from src.utils.constants import Direction, Color, GamePhase
from src.utils.logger import setup_logger, get_logger
from src.utils.types import Position, Velocity


class TestDirection:
    """Test Direction enum."""

    def test_direction_values(self) -> None:
        """Test direction delta values."""
        assert Direction.UP.dx == 0
        assert Direction.UP.dy == -1
        assert Direction.DOWN.dx == 0
        assert Direction.DOWN.dy == 1
        assert Direction.LEFT.dx == -1
        assert Direction.LEFT.dy == 0
        assert Direction.RIGHT.dx == 1
        assert Direction.RIGHT.dy == 0

    def test_direction_opposite(self) -> None:
        """Test direction opposite calculation."""
        assert Direction.UP.opposite() == Direction.DOWN
        assert Direction.DOWN.opposite() == Direction.UP
        assert Direction.LEFT.opposite() == Direction.RIGHT
        assert Direction.RIGHT.opposite() == Direction.LEFT
        assert Direction.NONE.opposite() == Direction.NONE


class TestColors:
    """Test Color enum."""

    def test_colors_exist(self) -> None:
        """Test that expected colors exist."""
        assert Color.BLACK.value == (0, 0, 0)
        assert Color.WHITE.value == (255, 255, 255)
        assert Color.RED.value == (255, 0, 0)


class TestGamePhase:
    """Test GamePhase enum."""

    def test_game_phases_exist(self) -> None:
        """Test that expected game phases exist."""
        assert GamePhase.MENU.value == 0
        assert GamePhase.PLAYING.value == 1
        assert GamePhase.PAUSED.value == 2


class TestTypes:
    """Test type aliases."""

    def test_position_type(self) -> None:
        """Test Position type."""
        pos: Position = (10, 20)
        assert pos == (10, 20)

    def test_velocity_type(self) -> None:
        """Test Velocity type."""
        vel: Velocity = (1, -1)
        assert vel == (1, -1)


class TestLogger:
    """Test logger setup."""

    def test_setup_logger(self) -> None:
        """Test logger setup."""
        logger = setup_logger("test_logger", use_colors=False)
        assert logger is not None
        assert logger.name == "test_logger"

    def test_get_logger(self) -> None:
        """Test get logger."""
        logger = get_logger("test_logger2")
        assert logger is not None
        assert logger.name == "test_logger2"
