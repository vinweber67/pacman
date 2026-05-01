"""Instructions scene."""

from __future__ import annotations

from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class InstructionsScene(Scene):
    """Display controls and basic rules."""

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
        """Render instructions text."""
        renderer.clear((15, 20, 35))
        renderer.draw_text(30, 30, "INSTRUCTIONS", (255, 255, 0))
        renderer.draw_text(30, 70, "Move: WASD or Arrow Keys", (255, 255, 255))
        renderer.draw_text(30, 100, "Pause: P", (255, 255, 255))
        renderer.draw_text(30, 130, "Cheat skip level: C", (255, 255, 255))
        renderer.draw_text(30, 160, "Quit game: Q or ESC", (255, 255, 255))
        renderer.draw_text(
            30,
            210,
            "Eat all pellets to clear level.",
            (255, 255, 255),
        )
        renderer.draw_text(30, 250, "Press ESC to return", (220, 220, 220))

    def handle_input(self, key: int) -> None:
        """Input handled centrally by game manager."""
        del key
