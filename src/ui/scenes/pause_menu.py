"""Pause menu scene."""

from __future__ import annotations

import math
import time
from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class PauseMenuScene(Scene):
    """Pause menu scene representation."""

    def __init__(self) -> None:
        self.options = ["Resume", "Main Menu"]
        self.selected = 0
        self._anim_time = 0.0
        self._last_nav_key: int | None = None
        self._last_nav_time = 0.0
        self._nav_repeat_cooldown = 0.14

    def on_enter(self) -> None:
        """Prepare active selections on start."""
        self.selected = 0
        self._anim_time = 0.0
        self._last_nav_key = None
        self._last_nav_time = 0.0

    def on_exit(self) -> None:
        """Cleanup when exiting menu."""
        return None

    def update(self, delta_time: float) -> None:
        """Updates animation clocks."""
        self._anim_time += max(0.0, delta_time)

    def render(self, renderer: Renderer) -> None:
        """Draw options centered on screen."""
        # 1. Dark semi-transparent full-screen overlay
        renderer.draw_transparent_overlay((10, 12, 28, 190))

        # 2. Draw centered dialog card
        card_w = 380
        card_h = 240
        card_x = (renderer.width - card_w) // 2
        card_y = (renderer.height - card_h) // 2

        # Glowing cyan border
        pulse = (math.sin(self._anim_time * 6.0) + 1.0) / 2.0
        glow_c = int(140 + 115 * pulse)

        # Double border
        renderer.draw_rect(
            card_x - 3,
            card_y - 3,
            card_w + 6,
            card_h + 6,
            (0, glow_c, 255),
        )
        renderer.draw_rect(card_x, card_y, card_w, card_h, (15, 20, 36))

        # Title
        title_text = "PAUSED"
        renderer.draw_text(
            card_x + (card_w - 140) // 2,
            card_y + 30,
            title_text,
            (255, 230, 0),
            size=36,
            font_name="Courier New",
            bold=True
        )

        # Options
        option_w = 260
        option_h = 42
        option_x = card_x + (card_w - option_w) // 2
        base_y = card_y + 95

        for index, option in enumerate(self.options):
            y = base_y + index * 60
            is_selected = index == self.selected

            if is_selected:
                border_color = (0, 255, 150)
                fill_color = (25, 45, 55)
                text_color = (255, 255, 255)
                # Pulsing outline
                renderer.draw_rect(
                    option_x - 2,
                    y - 2,
                    option_w + 4,
                    option_h + 4,
                    border_color,
                )
            else:
                border_color = (60, 60, 90)
                fill_color = (20, 22, 38)
                text_color = (160, 160, 190)

            renderer.draw_rect(option_x, y, option_w, option_h, fill_color)

            # Draw tiny pacman next to selection
            if is_selected:
                pac_cx = option_x + 20
                pac_cy = y + option_h // 2
                renderer.draw_circle(pac_cx, pac_cy, 8, (255, 220, 20))

            renderer.draw_text(
                option_x + 40,
                y + 10,
                option,
                text_color,
                size=18,
                bold=is_selected
            )

        # Footer help text
        renderer.draw_text(
            card_x + 50,
            card_y + card_h - 30,
            "Use W/S or Arrow Keys | Enter to Select",
            (100, 110, 140),
            size=12
        )

    def handle_input(self, key: int) -> None:
        """Forward input selections."""
        now = time.monotonic()
        is_nav = key in (65364, ord("s"), 65362, ord("w"))
        if (
            is_nav
            and self._last_nav_key == key
            and now - self._last_nav_time < self._nav_repeat_cooldown
        ):
            return

        if key in (65364, ord("s")):
            self.selected = (self.selected + 1) % len(self.options)
            self._last_nav_key = key
            self._last_nav_time = now
        elif key in (65362, ord("w")):
            self.selected = (self.selected - 1) % len(self.options)
            self._last_nav_key = key
            self._last_nav_time = now
