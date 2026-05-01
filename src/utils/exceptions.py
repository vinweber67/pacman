"""Custom exceptions for Pac-Man game."""


class PacmanError(Exception):
    """Base exception for all Pac-Man game errors."""


class ConfigError(PacmanError):
    """Raised when configuration loading or validation fails."""


class MazeGenerationError(PacmanError):
    """Raised when maze generation fails."""


class GameStateError(PacmanError):
    """Raised when game state is invalid."""


class RendererError(PacmanError):
    """Raised when rendering fails."""


class InputError(PacmanError):
    """Raised when input handling fails."""


class HighscoreError(PacmanError):
    """Raised when highscore operations fail."""
