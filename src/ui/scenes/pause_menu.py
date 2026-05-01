"""Pause menu scene."""

from __future__ import annotations

from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class PauseMenuScene(Scene):
    """Simple pause overlay scene."""

    def __init__(self) -> None:
        self.options = ["Resume", "Main Menu"]
        self.selected = 0

    def on_enter(self) -> None:
        """Reset selected option."""
        self.selected = 0

    def on_exit(self) -> None:
        """No-op exit hook."""
        return None

    def update(self, delta_time: float) -> None:
        """No animated state yet."""
        del delta_time

    def render(self, renderer: Renderer) -> None:
        """Render pause menu."""
        renderer.clear((5, 5, 15))
        renderer.draw_text(30, 30, "PAUSED", (255, 255, 0))
        renderer.draw_text(30, 60, "Use W/S + SPACE", (220, 220, 220))

        y = 120
        for index, option in enumerate(self.options):
            selected = index == self.selected
            box_color = (255, 255, 0) if selected else (70, 70, 120)
            text_color = (0, 0, 0) if selected else (255, 255, 255)
            renderer.draw_rect(30, y, 260, 36, box_color)
            renderer.draw_text(40, y + 8, option, text_color)
            y += 50

    def handle_input(self, key: int) -> None:
        """Handle up/down selection locally."""
        if key in (65364, ord("s")):
            self.selected = (self.selected + 1) % len(self.options)
        elif key in (65362, ord("w")):
            self.selected = (self.selected - 1) % len(self.options)
