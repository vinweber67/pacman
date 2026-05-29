"""Main menu scene."""

from __future__ import annotations

import math
import time
from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class MainMenuScene(Scene):
    """Simple main menu scene."""

    def __init__(self) -> None:
        self.options = [
            "Start Game",
            "View Highscores",
            "Instructions",
            "Exit",
        ]
        self.selected = 0
        self._anim_time = 0.0
        self._last_nav_key: int | None = None
        self._last_nav_time = 0.0
        self._nav_repeat_cooldown = 0.14

    def on_enter(self) -> None:
        """Prepare the menu."""
        self.selected = 0
        self._last_nav_key = None
        self._last_nav_time = 0.0

    def on_exit(self) -> None:
        """Cleanup for the menu."""
        return None

    def update(self, delta_time: float) -> None:
        """Menu animation updates."""
        self._anim_time += max(0.0, delta_time)

    def render(self, renderer: Renderer) -> None:
        """Render the menu background and options."""
        # 1. Neon Grid / Dark Blue Gradient Background
        for y in range(renderer.height):
            ratio = y / max(1, renderer.height - 1)
            # Blue-purple to deep dark gradient
            red = int(12 * (1.0 - ratio) + 4 * ratio)
            green = int(14 * (1.0 - ratio) + 4 * ratio)
            blue = int(45 * (1.0 - ratio) + 12 * ratio)
            renderer.draw_line(0, y, renderer.width, y, (red, green, blue), 1)

        # 2. Twinkling Stars / Grid
        for i in range(25):
            star_x = (i * 127 + 43) % renderer.width
            star_y = (i * 83 + 19) % (renderer.height - 120)
            twinkle = (
                0.3 + 0.7 * ((math.sin(self._anim_time * 2.5 + i) + 1.0) / 2.0)
            )
            size = 1 if twinkle < 0.65 else 2
            color = int(150 + 105 * twinkle)
            renderer.draw_circle(
                star_x,
                star_y,
                size,
                (color, color, min(255, color + 30)),
            )

        # 3. Big Glowing Title
        title_text = "P A C - M A N"
        title_y = 150
        # Calculate bounce
        bounce = int(math.sin(self._anim_time * 2.0) * 8)

        # Red/Blue offset shadows for a chromatic aberration/neon glow look
        renderer.draw_text(
            (renderer.width - 400) // 2 - 3,
            title_y + bounce + 2,
            title_text,
            (255, 0, 100),
            size=60,
            font_name="Courier New",
            bold=True
        )
        renderer.draw_text(
            (renderer.width - 400) // 2 + 3,
            title_y + bounce - 2,
            title_text,
            (0, 220, 255),
            size=60,
            font_name="Courier New",
            bold=True
        )
        # Main Yellow Title
        renderer.draw_text(
            (renderer.width - 400) // 2,
            title_y + bounce,
            title_text,
            (255, 230, 0),
            size=60,
            font_name="Courier New",
            bold=True
        )

        # Subtitle
        renderer.draw_text(
            (renderer.width - 240) // 2,
            240,
            "ARCADE CLASSIC REMAKE",
            (150, 180, 220),
            size=18,
            bold=True
        )

        # 4. Render Menu Options
        base_y = 350
        box_width = 380
        box_height = 48
        box_x = (renderer.width - box_width) // 2

        # Pulsating factor for selection highlights
        pulse = (math.sin(self._anim_time * 7.0) + 1.0) / 2.0

        for index, option in enumerate(self.options):
            y = base_y + index * 70
            is_selected = index == self.selected

            if is_selected:
                # Pulsing cyan/blue border
                glow_val = int(140 + 115 * pulse)
                border_color = (0, glow_val, 255)
                fill_color = (15, 30, 60)
                text_color = (255, 255, 255)

                # Draw selection box
                renderer.draw_rect(
                    box_x - 2,
                    y - 2,
                    box_width + 4,
                    box_height + 4,
                    border_color,
                )
                renderer.draw_rect(box_x, y, box_width, box_height, fill_color)

                # Selection indicator (A small Pac-man icon)
                pac_cx = box_x - 30
                pac_cy = y + box_height // 2
                renderer.draw_circle(pac_cx, pac_cy, 12, (255, 220, 20))
                # Pac-man mouth facing right
                openness = 0.2 + 0.2 * abs(math.sin(self._anim_time * 12.0))
                tip = (pac_cx + 14, pac_cy)
                p1 = (
                    pac_cx + int(12 * math.cos(openness)),
                    pac_cy - int(12 * math.sin(openness)),
                )
                p2 = (
                    pac_cx + int(12 * math.cos(openness)),
                    pac_cy + int(12 * math.sin(openness)),
                )
                renderer.draw_polygon(
                    [tip, p1, (pac_cx, pac_cy), p2], fill_color
                )
            else:
                border_color = (50, 50, 90)
                fill_color = (20, 20, 36)
                text_color = (180, 180, 210)

                # Draw standard box
                renderer.draw_rect(
                    box_x, y, box_width, box_height, border_color
                )
                renderer.draw_rect(
                    box_x + 2,
                    y + 2,
                    box_width - 4,
                    box_height - 4,
                    fill_color,
                )

            # Center text in box
            renderer.draw_text(
                box_x + 40,
                y + 12,
                option,
                text_color,
                size=22,
                font_name="Arial",
                bold=is_selected
            )

        # 5. Bottom Marquee Animation: Pac-Man chased by Blinky
        marquee_y = renderer.height - 100
        cycle = 10.0  # seconds to cross screen
        progress = (self._anim_time % cycle) / cycle

        # Pac-man X
        px = -60 + progress * (renderer.width + 200)

        # Draw Pac-Man
        pcx = int(px)
        pcy = marquee_y
        renderer.draw_circle(pcx, pcy, 20, (255, 220, 0))
        # mouth
        p_openness = 0.2 + 0.25 * abs(math.sin(self._anim_time * 15.0))
        p_tip = (pcx + 22, pcy)
        p_p1 = (
            pcx + int(20 * math.cos(p_openness)),
            pcy - int(20 * math.sin(p_openness)),
        )
        p_p2 = (
            pcx + int(20 * math.cos(p_openness)),
            pcy + int(20 * math.sin(p_openness)),
        )
        renderer.draw_polygon([p_tip, p_p1, (pcx, pcy), p_p2], (12, 12, 24))

        # Draw Red Ghost (Blinky) chasing behind
        g_offset = 70
        gx = int(px - g_offset)
        gy = marquee_y - 20
        g_bob = int(math.sin(self._anim_time * 8.0) * 4)

        # Red Ghost Body
        g_color = (255, 40, 40)
        renderer.draw_circle(gx + 20, gy + 20 + g_bob, 20, g_color)
        renderer.draw_rect(gx, gy + 20 + g_bob, 40, 20, g_color)
        # wavy bottom
        for j in range(3):
            wave_cx = gx + 6 + j * 14
            renderer.draw_circle(wave_cx, gy + 40 + g_bob, 7, g_color)

        # Ghost Eyes looking right
        renderer.draw_circle(gx + 12, gy + 16 + g_bob, 6, (255, 255, 255))
        renderer.draw_circle(gx + 28, gy + 16 + g_bob, 6, (255, 255, 255))
        # pupils
        renderer.draw_circle(gx + 15, gy + 16 + g_bob, 3, (20, 40, 180))
        renderer.draw_circle(gx + 31, gy + 16 + g_bob, 3, (20, 40, 180))

        # Info line at the bottom
        renderer.draw_text(
            (renderer.width - 300) // 2,
            renderer.height - 40,
            "W/S or Arrows to navigate  |  Enter to select  |  ESC to quit",
            (100, 110, 140),
            size=14,
            bold=False
        )

    def handle_input(self, key: int) -> None:
        """Handle keyboard navigation."""
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
