"""Gameplay scene."""

from __future__ import annotations

from src.game.game_state import GameState
from src.maze.tile import TileType
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
        """Render maze, entities and HUD."""
        renderer.clear((0, 0, 0))

        maze = self.state.maze
        offset_x = 0
        offset_y = 40

        if maze is not None:
            maze_px_width = maze.width * TILE_SIZE
            maze_px_height = maze.height * TILE_SIZE
            offset_x = max(0, (renderer.width - maze_px_width) // 2)
            offset_y = max(40, (renderer.height - maze_px_height) // 2)

            for y in range(maze.height):
                for x in range(maze.width):
                    tile = maze.tiles[y][x]
                    tile_color = (15, 15, 15)
                    if tile == TileType.WALL:
                        tile_color = (0, 0, 180)
                    renderer.draw_rect(
                        offset_x + x * TILE_SIZE,
                        offset_y + y * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE,
                        tile_color,
                    )

        for pellet_x, pellet_y in self.state.pellet_positions:
            pellet_size = max(4, TILE_SIZE // 4)
            pellet_offset = (TILE_SIZE - pellet_size) // 2
            renderer.draw_rect(
                offset_x + pellet_x * TILE_SIZE + pellet_offset,
                offset_y + pellet_y * TILE_SIZE + pellet_offset,
                pellet_size,
                pellet_size,
                (255, 230, 120),
            )

        pacman_x, pacman_y = self.state.pacman_position
        renderer.draw_rect(
            offset_x + pacman_x * TILE_SIZE,
            offset_y + pacman_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
            (255, 255, 0),
        )

        ghost_colors = [
            (255, 0, 0),
            (255, 184, 255),
            (0, 255, 255),
            (255, 184, 82),
        ]
        for index, (ghost_x, ghost_y) in enumerate(self.state.ghost_positions):
            renderer.draw_rect(
                offset_x + ghost_x * TILE_SIZE,
                offset_y + ghost_y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE,
                ghost_colors[index % len(ghost_colors)],
            )

        hud_text = (
            f"Score:{self.state.score}  "
            f"Lives:{self.state.lives}  "
            f"Level:{self.state.current_level}  "
            f"Time:{self.state.level_time_remaining}"
        )
        renderer.draw_text(12, 12, hud_text, (255, 255, 255))

    def handle_input(self, key: int) -> None:
        """Gameplay input placeholder."""
        del key
