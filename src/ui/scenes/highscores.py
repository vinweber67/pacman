"""Highscores scene."""

from __future__ import annotations

import math
from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class HighscoresScene(Scene):
    """Display top scores from persistent storage."""

    def __init__(self) -> None:
        self.rows: list[str] = []
        self._anim_time = 0.0

    def set_rows(self, rows: list[str]) -> None:
        """Set preformatted rows to display."""
        self.rows = rows

    def on_enter(self) -> None:
        """No-op enter hook."""
        self._anim_time = 0.0

    def on_exit(self) -> None:
        """No-op exit hook."""
        return None

    def update(self, delta_time: float) -> None:
        """Updates animation clocks."""
        self._anim_time += max(0.0, delta_time)

    def render(self, renderer: Renderer) -> None:
        """Render highscores list."""
        # Gradient background
        for y in range(renderer.height):
            ratio = y / max(1, renderer.height - 1)
            red = int(10 * (1.0 - ratio) + 3 * ratio)
            green = int(12 * (1.0 - ratio) + 4 * ratio)
            blue = int(40 * (1.0 - ratio) + 14 * ratio)
            renderer.draw_line(0, y, renderer.width, y, (red, green, blue), 1)

        # Tech border
        border_color = (0, 100, 220)
        renderer.draw_rect(
            20, 20, renderer.width - 40, renderer.height - 40, border_color
        )
        renderer.draw_rect(
            24, 24, renderer.width - 48, renderer.height - 48, (6, 8, 20)
        )

        # Title
        renderer.draw_text(
            (renderer.width - 240) // 2,
            50,
            "LEADERBOARD",
            (255, 230, 0),
            size=36,
            font_name="Courier New",
            bold=True
        )

        # Table Card box
        card_w = 560
        card_h = 520
        card_x = (renderer.width - card_w) // 2
        card_y = 130
        renderer.draw_rect(card_x, card_y, card_w, card_h, (35, 45, 75))
        renderer.draw_rect(
            card_x + 2, card_y + 2, card_w - 4, card_h - 4, (12, 14, 26)
        )

        # Column Headers
        header_y = card_y + 20
        renderer.draw_text(
            card_x + 40, header_y, "RANK", (0, 220, 255), size=18, bold=True
        )
        renderer.draw_text(
            card_x + 180, header_y, "PLAYER", (0, 220, 255), size=18, bold=True
        )
        renderer.draw_text(
            card_x + 400, header_y, "SCORE", (0, 220, 255), size=18, bold=True
        )

        renderer.draw_line(
            card_x + 30,
            header_y + 30,
            card_x + card_w - 30,
            header_y + 30,
            (50, 70, 100),
            1,
        )

        if not self.rows:
            renderer.draw_text(
                card_x + (card_w - 200) // 2,
                card_y + 200,
                "No highscores yet.",
                (140, 150, 180),
                size=18
            )
        else:
            base_y = card_y + 70
            for index, row in enumerate(self.rows[:10]):
                y = base_y + index * 42

                # Parse the formatted row
                try:
                    if not isinstance(row, str):
                        raise TypeError("Highscore row must be a string")
                    rank_str = row[0:2].strip()
                    name_str = row[4:14].strip()
                    score_str = row[16:].strip()
                except (TypeError, ValueError, AttributeError, IndexError):
                    # Fallback if string structure changes
                    rank_str = f"{index + 1:02d}"
                    name_str = "PLAYER"
                    score_str = "0"

                # Color based on rank
                if index == 0:
                    text_color = (255, 215, 0)  # Gold
                    bold = True
                elif index == 1:
                    text_color = (200, 200, 200)  # Silver
                    bold = True
                elif index == 2:
                    text_color = (205, 127, 50)  # Bronze
                    bold = True
                else:
                    text_color = (180, 200, 255)  # Normal ranks
                    bold = False

                # Rank
                renderer.draw_text(
                    card_x + 40,
                    y + 8,
                    f"# {rank_str}",
                    text_color,
                    size=18,
                    bold=bold,
                )
                # Player Name
                renderer.draw_text(
                    card_x + 180,
                    y + 8,
                    name_str,
                    text_color,
                    size=18,
                    bold=bold,
                )
                # Score
                renderer.draw_text(
                    card_x + 400,
                    y + 8,
                    score_str,
                    text_color,
                    size=18,
                    bold=bold,
                )

        # Pulse for esc prompt
        pulse = (math.sin(self._anim_time * 5.0) + 1.0) / 2.0
        prompt_color = int(150 + 105 * pulse)

        renderer.draw_text(
            (renderer.width - 240) // 2,
            renderer.height - 80,
            "Press ESC or Q to return to Menu",
            (prompt_color, prompt_color, prompt_color),
            size=16,
            bold=True
        )

    def handle_input(self, key: int) -> None:
        """Input handled centrally by game manager."""
        del key
