"""Gameplay scene."""

from __future__ import annotations

import math

from src.game.game_state import GameState
from src.maze.maze import Maze
from src.maze.tile import TileType
from src.utils.constants import TILE_SIZE
from src.ui.renderer import Renderer
from src.ui.scenes.scene import Scene


class GameScene(Scene):
    """Gameplay scene with enriched visual rendering."""

    def __init__(self) -> None:
        self.state = GameState()
        self._anim_time = 0.0
        self._last_pacman_pos = self.state.pacman_position
        self._pacman_dir = (1, 0)

    def on_enter(self) -> None:
        """Prepare gameplay rendering state."""
        return None

    def on_exit(self) -> None:
        """Cleanup gameplay rendering state."""
        return None

    def update(self, delta_time: float) -> None:
        """Update visual animation clocks."""
        self._anim_time += max(0.0, delta_time)

    @staticmethod
    def _layout(renderer: Renderer, maze: Maze) -> tuple[int, int, int]:
        """Compute dynamic maze layout on screen."""
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
        return offset_x, offset_y, tile_size

    def _draw_background(self, renderer: Renderer) -> None:
        """Draw a subtle vertical gradient background."""
        for y in range(renderer.height):
            ratio = y / max(1, renderer.height - 1)
            red = int(8 + 12 * ratio)
            green = int(10 + 16 * ratio)
            blue = int(18 + 35 * ratio)
            renderer.draw_line(0, y, renderer.width, y, (red, green, blue), 1)

    def _draw_maze(
        self,
        renderer: Renderer,
        offset_x: int,
        offset_y: int,
        tile_size: int,
    ) -> None:
        """Draw floor tiles and walls with depth."""
        maze = self.state.maze
        if maze is None:
            return

        wall_color = (20, 92, 255)
        wall_glow = (90, 160, 255)
        wall_shadow = (8, 38, 120)
        floor_a = (11, 15, 30)
        floor_b = (13, 18, 34)
        thickness = max(1, tile_size // 8)

        has_wall_mask = (
            len(maze.wall_mask) == maze.height
            and all(len(row) == maze.width for row in maze.wall_mask)
        )

        for y in range(maze.height):
            for x in range(maze.width):
                px = offset_x + x * tile_size
                py = offset_y + y * tile_size

                floor_color = floor_a if (x + y) % 2 == 0 else floor_b
                renderer.draw_rect(px, py, tile_size, tile_size, floor_color)

                if has_wall_mask:
                    mask = maze.wall_mask[y][x]
                    if mask & 1:
                        renderer.draw_rect(
                            px,
                            py,
                            tile_size,
                            thickness,
                            wall_color,
                        )
                        renderer.draw_rect(
                            px,
                            py,
                            tile_size,
                            max(1, thickness // 2),
                            wall_glow,
                        )
                    if mask & 2:
                        renderer.draw_rect(
                            px + tile_size - thickness,
                            py,
                            thickness,
                            tile_size,
                            wall_color,
                        )
                        renderer.draw_rect(
                            px + tile_size - max(1, thickness // 2),
                            py,
                            max(1, thickness // 2),
                            tile_size,
                            wall_shadow,
                        )
                    if mask & 4:
                        renderer.draw_rect(
                            px,
                            py + tile_size - thickness,
                            tile_size,
                            thickness,
                            wall_color,
                        )
                        renderer.draw_rect(
                            px,
                            py + tile_size - max(1, thickness // 2),
                            tile_size,
                            max(1, thickness // 2),
                            wall_shadow,
                        )
                    if mask & 8:
                        renderer.draw_rect(
                            px,
                            py,
                            thickness,
                            tile_size,
                            wall_color,
                        )
                        renderer.draw_rect(
                            px,
                            py,
                            max(1, thickness // 2),
                            tile_size,
                            wall_glow,
                        )
                elif maze.tiles[y][x] == TileType.WALL:
                    renderer.draw_rect(
                        px,
                        py,
                        tile_size,
                        tile_size,
                        (10, 35, 160),
                    )

    def _draw_pellets(
        self,
        renderer: Renderer,
        offset_x: int,
        offset_y: int,
        tile_size: int,
    ) -> None:
        """Draw classic pellets and animated super pellets."""
        for pellet_x, pellet_y in self.state.pellet_positions:
            cx = offset_x + pellet_x * tile_size + tile_size // 2
            cy = offset_y + pellet_y * tile_size + tile_size // 2
            radius = max(2, tile_size // 8)
            renderer.draw_circle(cx, cy, radius + 1, (255, 245, 190))
            renderer.draw_circle(cx, cy, radius, (255, 230, 130))

        pulse = (math.sin(self._anim_time * 6.0) + 1.0) / 2.0
        for pellet_x, pellet_y in self.state.super_pellet_positions:
            cx = offset_x + pellet_x * tile_size + tile_size // 2
            cy = offset_y + pellet_y * tile_size + tile_size // 2
            base = max(4, tile_size // 4)
            radius = int(base + pulse * max(2, tile_size // 10))
            renderer.draw_circle(cx, cy, radius + 4, (80, 110, 180))
            renderer.draw_circle(cx, cy, radius + 1, (220, 240, 255))
            renderer.draw_circle(cx, cy, radius, (255, 255, 255))

    def _update_pacman_facing(self) -> None:
        """Track Pac-Man direction from movement deltas."""
        current = self.state.pacman_position
        dx = current[0] - self._last_pacman_pos[0]
        dy = current[1] - self._last_pacman_pos[1]
        if dx > 0:
            self._pacman_dir = (1, 0)
        elif dx < 0:
            self._pacman_dir = (-1, 0)
        elif dy > 0:
            self._pacman_dir = (0, 1)
        elif dy < 0:
            self._pacman_dir = (0, -1)
        self._last_pacman_pos = current

    def _draw_pacman(
        self,
        renderer: Renderer,
        offset_x: int,
        offset_y: int,
        tile_size: int,
    ) -> None:
        """Draw Pac-Man with a simple mouth animation."""
        self._update_pacman_facing()
        pacman_x, pacman_y = self.state.pacman_position
        cx = offset_x + pacman_x * tile_size + tile_size // 2
        cy = offset_y + pacman_y * tile_size + tile_size // 2
        radius = max(4, tile_size // 2 - 1)

        renderer.draw_circle(cx, cy, radius, (255, 220, 20))
        renderer.draw_circle(
            cx - radius // 4,
            cy - radius // 4,
            1,
            (140, 90, 10),
        )

        openness = 0.16 + 0.24 * abs(math.sin(self._anim_time * 10.0))
        mx, my = self._pacman_dir
        tip = (cx + int(mx * (radius + 2)), cy + int(my * (radius + 2)))
        side_x = -my
        side_y = mx
        spread = int(radius * openness)
        p1 = (
            cx + int(mx * radius + side_x * spread),
            cy + int(my * radius + side_y * spread),
        )
        p2 = (
            cx + int(mx * radius - side_x * spread),
            cy + int(my * radius - side_y * spread),
        )
        renderer.draw_polygon(
            [tip, p1, (cx, cy), p2],
            (10, 10, 22),
        )

    def _draw_ghosts(
        self,
        renderer: Renderer,
        offset_x: int,
        offset_y: int,
        tile_size: int,
    ) -> None:
        """Draw ghosts with body, eyes and pupils."""
        ghost_colors = [
            (255, 60, 60),
            (255, 170, 235),
            (120, 240, 255),
            (255, 185, 70),
        ]
        for index, (ghost_x, ghost_y) in enumerate(self.state.ghost_positions):
            gx = offset_x + ghost_x * tile_size
            gy = offset_y + ghost_y * tile_size
            color = ghost_colors[index % len(ghost_colors)]

            radius = max(4, tile_size // 2)
            center_x = gx + tile_size // 2
            center_y = gy + max(3, tile_size // 2 - 1)

            renderer.draw_circle(center_x, center_y, radius, color)
            renderer.draw_rect(
                gx,
                gy + tile_size // 2,
                tile_size,
                tile_size // 2,
                color,
            )

            eye_y = gy + max(3, tile_size // 2)
            left_eye_x = gx + tile_size // 3
            right_eye_x = gx + (2 * tile_size) // 3
            eye_r = max(2, tile_size // 6)
            pupil_r = max(1, eye_r // 2)
            renderer.draw_circle(left_eye_x, eye_y, eye_r, (255, 255, 255))
            renderer.draw_circle(right_eye_x, eye_y, eye_r, (255, 255, 255))
            renderer.draw_circle(left_eye_x + 1, eye_y, pupil_r, (20, 40, 180))
            renderer.draw_circle(
                right_eye_x + 1,
                eye_y,
                pupil_r,
                (20, 40, 180),
            )

    def _draw_hud(self, renderer: Renderer) -> None:
        """Draw top HUD with panel background."""
        renderer.draw_rect(0, 0, renderer.width, 44, (12, 14, 24))
        renderer.draw_line(0, 44, renderer.width, 44, (40, 80, 160), 2)

        hud_text = (
            f"Score:{self.state.score}  "
            f"Lives:{self.state.lives}  "
            f"Level:{self.state.current_level}  "
            f"Time:{self.state.level_time_remaining}"
        )
        renderer.draw_text(12, 10, hud_text, (240, 240, 255))
        renderer.draw_text(
            12,
            28,
            "Move: WASD/Arrows | Pause: P | Quit: Q/ESC",
            (170, 178, 205),
        )

    def render(self, renderer: Renderer) -> None:
        """Render maze, entities and HUD with improved details."""
        renderer.clear((8, 10, 20))
        self._draw_background(renderer)

        maze = self.state.maze
        offset_x = 0
        offset_y = 40
        tile_size = TILE_SIZE

        if maze is not None:
            offset_x, offset_y, tile_size = self._layout(renderer, maze)
            self._draw_maze(renderer, offset_x, offset_y, tile_size)

        self._draw_pellets(renderer, offset_x, offset_y, tile_size)
        self._draw_pacman(renderer, offset_x, offset_y, tile_size)
        self._draw_ghosts(renderer, offset_x, offset_y, tile_size)
        self._draw_hud(renderer)

    def handle_input(self, key: int) -> None:
        """Gameplay input placeholder."""
        del key
