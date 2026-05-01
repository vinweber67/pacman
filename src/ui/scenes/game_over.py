"""Game over/victory scene."""

from __future__ import annotations

from typing import Optional

from src.game.game_state import GameState
from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class GameOverScene(Scene):
    """Display end-of-run summary."""

    def __init__(self) -> None:
        self.state = GameState()
        self.title = "GAME OVER"
        self.subtitle = "Enter your name (max 10) then press ENTER"
        self.player_name = ""
        self._submitted_name: Optional[str] = None

    def set_title(self, title: str) -> None:
        """Set scene title."""
        self.title = title

    def consume_submitted_name(self) -> Optional[str]:
        """Consume and return submitted player name if available."""
        submitted_name = self._submitted_name
        self._submitted_name = None
        return submitted_name

    def on_enter(self) -> None:
        """Reset name prompt state."""
        self.player_name = ""
        self._submitted_name = None

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
        renderer.draw_text(30, 75, f"Final score: {self.state.score}",
                           (255, 255, 255))
        renderer.draw_text(30, 105, self.subtitle, (220, 220, 220))
        shown_name = self.player_name if self.player_name else "_"
        renderer.draw_rect(30, 145, 320, 38, (35, 35, 70))
        renderer.draw_text(40, 155, shown_name, (255, 255, 255))
        renderer.draw_text(30, 205, "ESC: save as PLAYER", (180, 180, 180))

    def handle_input(self, key: int) -> None:
        """Handle typed player name and submission."""
        if key in (13, ord("\r"), ord(" ")):
            if self.player_name.strip():
                self._submitted_name = self.player_name.strip()
            else:
                self._submitted_name = "PLAYER"
            return

        if key in (8, 127):
            self.player_name = self.player_name[:-1]
            return

        if key in (27, 65307):
            self._submitted_name = "PLAYER"
            return

        if len(self.player_name) >= 10:
            return

        if 32 <= key <= 126:
            char = chr(key)
            if char.isalnum() or char == " ":
                self.player_name += char
