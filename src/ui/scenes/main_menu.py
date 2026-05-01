"""Main menu scene."""

from __future__ import annotations

from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class MainMenuScene(Scene):
    """Simple main menu scene."""

    def __init__(self) -> None:
        self.options = ["Start Game", "Highscores", "Instructions", "Exit"]
        self.selected = 0

    def on_enter(self) -> None:
        """Prepare the menu."""
        self.selected = 0

    def on_exit(self) -> None:
        """Cleanup for the menu."""
        return None

    def update(self, delta_time: float) -> None:
        """Menu animation placeholder."""
        del delta_time

    def render(self, renderer: Renderer) -> None:
        """Render the menu background."""
        renderer.clear((0, 0, 0))

    def handle_input(self, key: int) -> None:
        """Handle keyboard navigation."""
        if key in (65364, ord("s")):
            self.selected = (self.selected + 1) % len(self.options)
        elif key in (65362, ord("w")):
            self.selected = (self.selected - 1) % len(self.options)
