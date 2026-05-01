"""Game over/victory scene."""

from __future__ import annotations

from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class GameOverScene(Scene):
    """Display end-of-run summary."""

    def __init__(self) -> None:
        self.title = "GAME OVER"
        self.subtitle = "Press ESC to return to menu"

    def set_title(self, title: str) -> None:
        """Set scene title."""
        self.title = title

    def on_enter(self) -> None:
        """No-op enter hook."""
        return None

    def on_exit(self) -> None:
        """No-op exit hook."""
        return None

    def update(self, delta_time: float) -> None:
        """No animated state yet."""
        del delta_time

    def render(self, renderer: Renderer) -> None:
        """Render game over screen."""
        renderer.clear((20, 0, 0))
        renderer.draw_text(30, 30, self.title, (255, 255, 0))
        renderer.draw_text(30, 80, self.subtitle, (220, 220, 220))

    def handle_input(self, key: int) -> None:
        """Input handled centrally by game manager."""
        del key
