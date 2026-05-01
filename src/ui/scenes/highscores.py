"""Highscores scene."""

from __future__ import annotations

from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class HighscoresScene(Scene):
    """Display top scores from persistent storage."""

    def __init__(self) -> None:
        self.rows: list[str] = []

    def set_rows(self, rows: list[str]) -> None:
        """Set preformatted rows to display."""
        self.rows = rows

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
        """Render highscores list."""
        renderer.clear((20, 10, 30))
        renderer.draw_text(30, 30, "HIGHSCORES", (255, 255, 0))
        renderer.draw_text(30, 60, "Press ESC to return", (220, 220, 220))

        if not self.rows:
            renderer.draw_text(30, 110, "No highscores yet.", (255, 255, 255))
            return

        y = 110
        for row in self.rows[:10]:
            renderer.draw_text(30, y, row, (255, 255, 255))
            y += 28

    def handle_input(self, key: int) -> None:
        """Input handled centrally by game manager."""
        del key
