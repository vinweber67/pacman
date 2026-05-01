"""Base scene class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.ui.renderer import Renderer


class Scene(ABC):
    """Base class for all scenes."""

    @abstractmethod
    def on_enter(self) -> None:
        """Called when the scene becomes active."""
        raise NotImplementedError

    @abstractmethod
    def on_exit(self) -> None:
        """Called when the scene becomes inactive."""
        raise NotImplementedError

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update the scene."""
        raise NotImplementedError

    @abstractmethod
    def render(self, renderer: Renderer) -> None:
        """Render the scene."""
        raise NotImplementedError

    @abstractmethod
    def handle_input(self, key: int) -> None:
        """Handle user input."""
        raise NotImplementedError
