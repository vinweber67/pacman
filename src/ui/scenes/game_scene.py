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
        tile_size = TILE_SIZE

        if maze is not None:
            horizontal_padding = 12
            top_hud_height = 48
            bottom_padding = 12
            available_width = max(1, renderer.width - 2 * horizontal_padding)
            available_height = max(
                1,
                renderer.height - top_hud_height - bottom_padding,
            )
            tile_size = max(
                8,
                min(
                    available_width // max(1, maze.width),
                    available_height // max(1, maze.height),
                ),
            )
            maze_px_width = maze.width * tile_size
            maze_px_height = maze.height * tile_size
            offset_x = max(
                horizontal_padding,
                (renderer.width - maze_px_width) // 2,
            )
            offset_y = max(
                top_hud_height,
                top_hud_height + (available_height - maze_px_height) // 2,
            )
            wall_thickness = max(1, tile_size // 8)
            has_wall_mask = (
                len(maze.wall_mask) == maze.height
                and all(len(row) == maze.width for row in maze.wall_mask)
            )

            for y in range(maze.height):
                for x in range(maze.width):
                    px = offset_x + x * tile_size
                    py = offset_y + y * tile_size
                    renderer.draw_rect(
                        px,
                        py,
                        tile_size,
                        tile_size,
                        (10, 10, 20),
                    )

                    if has_wall_mask:
                        mask = maze.wall_mask[y][x]
                        if mask & 1:  # north
                            renderer.draw_rect(
                                px,
                                py,
                                tile_size,
                                wall_thickness,
                                (0, 50, 255),
                            )
                        if mask & 2:  # east
                            renderer.draw_rect(
                                px + tile_size - wall_thickness,
                                py,
                                wall_thickness,
                                tile_size,
                                (0, 50, 255),
                            )
                        if mask & 4:  # south
                            renderer.draw_rect(
                                px,
                                py + tile_size - wall_thickness,
                                tile_size,
                                wall_thickness,
                                (0, 50, 255),
                            )
                        if mask & 8:  # west
                            renderer.draw_rect(
                                px,
                                py,
                                wall_thickness,
                                tile_size,
                                (0, 50, 255),
                            )
                    elif maze.tiles[y][x] == TileType.WALL:
                        renderer.draw_rect(
                            px,
                            py,
                            tile_size,
                            tile_size,
                            (0, 0, 180),
                        )

        for pellet_x, pellet_y in self.state.pellet_positions:
            pellet_size = max(4, tile_size // 5)
            pellet_offset = (tile_size - pellet_size) // 2
            renderer.draw_rect(
                offset_x + pellet_x * tile_size + pellet_offset,
                offset_y + pellet_y * tile_size + pellet_offset,
                pellet_size,
                pellet_size,
                (255, 230, 120),
            )

        for pellet_x, pellet_y in self.state.super_pellet_positions:
            super_size = max(6, tile_size // 2)
            super_offset = (tile_size - super_size) // 2
            renderer.draw_rect(
                offset_x + pellet_x * tile_size + super_offset,
                offset_y + pellet_y * tile_size + super_offset,
                super_size,
                super_size,
                (255, 255, 255),
            )

        pacman_x, pacman_y = self.state.pacman_position
        renderer.draw_rect(
            offset_x + pacman_x * tile_size,
            offset_y + pacman_y * tile_size,
            tile_size,
            tile_size,
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
                offset_x + ghost_x * tile_size,
                offset_y + ghost_y * tile_size,
                tile_size,
                tile_size,
                ghost_colors[index % len(ghost_colors)],
            )

        hud_text = (
            f"Score:{self.state.score}  "
            f"Lives:{self.state.lives}  "
            f"Level:{self.state.current_level}  "
            f"Time:{self.state.level_time_remaining}"
        )
        renderer.draw_text(12, 12, hud_text, (255, 255, 255))
        renderer.draw_text(
            12,
            28,
            "Move: WASD/Arrows | Pause: P | Quit: Q/ESC",
            (180, 180, 180),
        )

    def handle_input(self, key: int) -> None:
        """Gameplay input placeholder."""
        del key
