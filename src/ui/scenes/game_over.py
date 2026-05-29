"""Game over and entry scene."""

from __future__ import annotations

import math
from typing import Optional

from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class GameOverScene(Scene):
    """Allow players to submit highscores on death."""

    def __init__(self) -> None:
        self.message = "GAME OVER"
        self.player_name = ""
        self._submitted_name: Optional[str] = None
        self._anim_time = 0.0

    def set_message(self, message: str) -> None:
        """Dynamically update header messages."""
        self.message = message

    def consume_submitted_name(self) -> Optional[str]:
        """Pop the submitted player name back to manager."""
        name = self._submitted_name
        self._submitted_name = None
        return name

    def on_enter(self) -> None:
        """Reset input buffers on entry."""
        self.player_name = ""
        self._submitted_name = None
        self._anim_time = 0.0

    def on_exit(self) -> None:
        """No-op exit hook."""
        return None

    def update(self, delta_time: float) -> None:
        """Updates animation clocks."""
        self._anim_time += max(0.0, delta_time)

    def render(self, renderer: Renderer) -> None:
        """Draw final score stats and input forms."""
        # 1. Overlay color: Reddish for Game Over, Greenish for Victory
        is_victory = "VICTORY" in self.message or "WIN" in self.message
        if is_victory:
            renderer.draw_transparent_overlay((8, 30, 20, 195))
            border_color = (0, 255, 120)
        else:
            renderer.draw_transparent_overlay((32, 10, 10, 195))
            border_color = (255, 40, 40)

        # 2. Draw dialog card
        card_w = 440
        card_h = 280
        card_x = (renderer.width - card_w) // 2
        card_y = (renderer.height - card_h) // 2

        # Glowing outline
        pulse = (math.sin(self._anim_time * 6.5) + 1.0) / 2.0
        glow_val = int(140 + 115 * pulse)
        border_pulse_color = (
            int(border_color[0] * (glow_val / 255.0)),
            int(border_color[1] * (glow_val / 255.0)),
            int(border_color[2] * (glow_val / 255.0)),
        )

        renderer.draw_rect(
            card_x - 3,
            card_y - 3,
            card_w + 6,
            card_h + 6,
            border_pulse_color,
        )
        renderer.draw_rect(card_x, card_y, card_w, card_h, (18, 16, 22))

        # 3. Header Message
        renderer.draw_text(
            card_x + (card_w - 240) // 2,
            card_y + 35,
            self.message,
            border_color,
            size=36
        )

        # 4. Form text
        renderer.draw_text(
            card_x + 50,
            card_y + 95,
            "ENTER PLAYER NAME",
            (200, 200, 220),
            size=18
        )

        # Input field box
        field_w = 340
        field_h = 44
        field_x = card_x + 50
        field_y = card_y + 130
        renderer.draw_rect(field_x, field_y, field_w, field_h, (50, 50, 75))
        renderer.draw_rect(
            field_x + 2,
            field_y + 2,
            field_w - 4,
            field_h - 4,
            (12, 10, 16),
        )

        # Text with blinking cursor
        blink_cursor = ""
        if int(self._anim_time * 2.0) % 2 == 0:
            blink_cursor = "_"
        display_name = self.player_name + blink_cursor

        renderer.draw_text(
            field_x + 15,
            field_y + 10,
            display_name,
            (255, 230, 0),
            size=22
        )

        # 5. Prompts
        renderer.draw_text(
            card_x + 50,
            card_y + 200,
            "Press ENTER to save score",
            (140, 150, 180),
            size=14
        )
        renderer.draw_text(
            card_x + 50,
            card_y + 230,
            "Press ESC to skip saving",
            (110, 120, 140),
            size=14
        )

    def handle_input(self, key: int) -> None:
        """Grow name buffer or trigger submission."""
        # Enter
        if key in (10, 13, ord("\r")):
            name = self.player_name.strip()
            self._submitted_name = name if name else "PLAYER"
            return

        # Backspace
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
