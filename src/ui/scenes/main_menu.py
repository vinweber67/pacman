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
        """Render the menu background and options."""
        renderer.clear((10, 10, 30))
        renderer.draw_text(30, 30, "PAC-MAN", (255, 255, 0))
        renderer.draw_text(30, 60, "Use W/S or arrows", (220, 220, 220))

        base_y = 120
        for index, option in enumerate(self.options):
            y = base_y + index * 50
            is_selected = index == self.selected
            box_color = (255, 255, 0) if is_selected else (70, 70, 120)
            text_color = (0, 0, 0) if is_selected else (255, 255, 255)
            renderer.draw_rect(30, y, 300, 36, box_color)
            renderer.draw_text(40, y + 8, option, text_color)

    def handle_input(self, key: int) -> None:
        """Handle keyboard navigation."""
        if key in (65364, ord("s")):
            self.selected = (self.selected + 1) % len(self.options)
        elif key in (65362, ord("w")):
            self.selected = (self.selected - 1) % len(self.options)
