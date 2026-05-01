"""Custom exceptions for Pac-Man game."""


class PacmanError(Exception):
    """Base exception for all Pac-Man game errors."""

    pass


class ConfigError(PacmanError):
    """Raised when configuration loading or validation fails."""

    pass


class MazeGenerationError(PacmanError):
    """Raised when maze generation fails."""

    pass


class GameStateError(PacmanError):
    """Raised when game state is invalid."""

    pass


class RendererError(PacmanError):
    """Raised when rendering fails."""

    pass


class InputError(PacmanError):
    """Raised when input handling fails."""

    pass


class HighscoreError(PacmanError):
    """Raised when highscore operations fail."""

    pass
