"""Gameplay scene."""

from __future__ import annotations

from src.game.game_state import GameState
from src.utils.constants import TILE_SIZE
from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class GameScene(Scene):
    """Minimal gameplay scene used by the loop integration."""

    def __init__(self) -> None:
        self.state = GameState()

    def on_enter(self) -> None:
        """Prepare gameplay rendering state."""
        return None

    def on_exit(self) -> None:
        """Cleanup gameplay rendering state."""
        return None

    def update(self, delta_time: float) -> None:
        """Gameplay update placeholder."""
        del delta_time

    def render(self, renderer: Renderer) -> None:
        """Render a basic gameplay frame with HUD and entities."""
        renderer.clear((0, 0, 0))

        # Decorative frame
        renderer.draw_rect(0, 0, renderer.width, 4, (0, 0, 255))
        renderer.draw_rect(0, renderer.height - 4, renderer.width, 4, (0, 0, 255))
        renderer.draw_rect(0, 0, 4, renderer.height, (0, 0, 255))
        renderer.draw_rect(renderer.width - 4, 0, 4, renderer.height, (0, 0, 255))

        # Pac-Man
        pacman_x, pacman_y = self.state.pacman_position
        renderer.draw_rect(
            pacman_x * TILE_SIZE,
            pacman_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
            (255, 255, 0),
        )

        # Ghosts
        ghost_colors = [
            (255, 0, 0),
            (255, 184, 255),
            (0, 255, 255),
            (255, 184, 82),
        ]
        for index, (ghost_x, ghost_y) in enumerate(self.state.ghost_positions):
            renderer.draw_rect(
                ghost_x * TILE_SIZE,
                ghost_y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE,
                ghost_colors[index % len(ghost_colors)],
            )

        # HUD text
        hud_text = (
            f"Score:{self.state.score}  "
            f"Lives:{self.state.lives}  "
            f"Level:{self.state.current_level}  "
            f"Time:{self.state.level_time_remaining}"
        )
        renderer.draw_text(12, 20, hud_text, (255, 255, 255))

    def handle_input(self, key: int) -> None:
        """Gameplay input placeholder."""
        del key
