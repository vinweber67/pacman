"""Instructions scene."""

from __future__ import annotations

import math
from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class InstructionsScene(Scene):
    """Display controls and basic rules."""

    def __init__(self) -> None:
        self._anim_time = 0.0

    def on_enter(self) -> None:
        """No-op enter hook."""
        return None

    def on_exit(self) -> None:
        """No-op exit hook."""
        return None

    def update(self, delta_time: float) -> None:
        """Update animation clocks."""
        self._anim_time += max(0.0, delta_time)

    def render(self, renderer: Renderer) -> None:
        """Render instructions text."""
        # Dark Cyber Gradient background
        for y in range(renderer.height):
            ratio = y / max(1, renderer.height - 1)
            red = int(8 * (1.0 - ratio) + 2 * ratio)
            green = int(10 * (1.0 - ratio) + 6 * ratio)
            blue = int(35 * (1.0 - ratio) + 16 * ratio)
            renderer.draw_line(0, y, renderer.width, y, (red, green, blue), 1)

        # 2. Tech lines/grid border
        border_color = (0, 100, 220)
        renderer.draw_rect(
            20, 20, renderer.width - 40, renderer.height - 40, border_color
        )
        renderer.draw_rect(
            24, 24, renderer.width - 48, renderer.height - 48, (5, 8, 20)
        )

        # Title
        renderer.draw_text(
            (renderer.width - 320) // 2,
            50,
            "INSTRUCTIONS",
            (255, 230, 0),
            size=36,
            font_name="Courier New",
            bold=True
        )

        # Pulse for prompt
        pulse = (math.sin(self._anim_time * 5.0) + 1.0) / 2.0
        prompt_color = int(160 + 95 * pulse)

        # Control cards
        card_width = 340
        card_height = 140

        # Left Column - Controls
        col1_x = 60
        y_controls = 140

        renderer.draw_rect(
            col1_x, y_controls, card_width, card_height, (40, 60, 120)
        )
        renderer.draw_rect(
            col1_x + 2,
            y_controls + 2,
            card_width - 4,
            card_height - 4,
            (12, 14, 28),
        )
        renderer.draw_text(
            col1_x + 15,
            y_controls + 12,
            "CONTROLS",
            (0, 220, 255),
            size=20,
            bold=True,
        )
        renderer.draw_text(
            col1_x + 15,
            y_controls + 45,
            "Move: WASD or Arrow Keys",
            (255, 255, 255),
            size=16,
        )
        renderer.draw_text(
            col1_x + 15,
            y_controls + 75,
            "Pause Game: P",
            (255, 255, 255),
            size=16,
        )
        renderer.draw_text(
            col1_x + 15,
            y_controls + 105,
            "Quit Game: Q or ESC",
            (255, 255, 255),
            size=16,
        )

        # Right Column - Gameplay Rules
        col2_x = renderer.width - card_width - 60

        renderer.draw_rect(
            col2_x, y_controls, card_width, card_height, (40, 60, 120)
        )
        renderer.draw_rect(
            col2_x + 2,
            y_controls + 2,
            card_width - 4,
            card_height - 4,
            (12, 14, 28),
        )
        renderer.draw_text(
            col2_x + 15,
            y_controls + 12,
            "RULES",
            (255, 100, 180),
            size=20,
            bold=True,
        )
        renderer.draw_text(
            col2_x + 15,
            y_controls + 45,
            "Eat all pellets to advance.",
            (255, 255, 255),
            size=16,
        )
        renderer.draw_text(
            col2_x + 15,
            y_controls + 75,
            "Super pacgums freeze/scare ghosts.",
            (255, 255, 255),
            size=16,
        )
        renderer.draw_text(
            col2_x + 15,
            y_controls + 105,
            "Avoid ghosts to survive!",
            (255, 255, 255),
            size=16,
        )

        # Bottom Card - Cheats Reference
        cheat_card_w = renderer.width - 120
        cheat_card_h = 190
        y_cheats = 310
        renderer.draw_rect(
            60, y_cheats, cheat_card_w, cheat_card_h, (90, 80, 40)
        )
        renderer.draw_rect(
            62,
            y_cheats + 2,
            cheat_card_w - 4,
            cheat_card_h - 4,
            (20, 18, 12),
        )

        renderer.draw_text(
            80,
            y_cheats + 15,
            "CHEAT CODE REFERENCE",
            (255, 220, 20),
            size=20,
            bold=True,
        )

        cheat_col1 = [
            "C : Skip Level / Advance",
            "I : Toggle Invincibility",
            "G : Toggle Freeze Ghosts",
        ]
        cheat_col2 = [
            "T : Toggle Level Timer",
            "L : Gain Extra Life",
            "K : Multiply Movement Speed",
        ]
        cheat_col3 = [
            "V : Draw Path Overlays",
            "H : Toggle Help Panel",
        ]

        for idx, text in enumerate(cheat_col1):
            renderer.draw_text(
                80, y_cheats + 55 + idx * 35, text, (230, 220, 200), size=16
            )
        for idx, text in enumerate(cheat_col2):
            renderer.draw_text(
                340, y_cheats + 55 + idx * 35, text, (230, 220, 200), size=16
            )
        for idx, text in enumerate(cheat_col3):
            renderer.draw_text(
                600, y_cheats + 55 + idx * 35, text, (230, 220, 200), size=16
            )

        # Return Prompt
        renderer.draw_text(
            (renderer.width - 260) // 2,
            renderer.height - 80,
            "Press ESC or Q to return to Menu",
            (prompt_color, prompt_color, prompt_color),
            size=18,
            bold=True,
        )

    def handle_input(self, key: int) -> None:
        """Input handled centrally by game manager."""
        del key
