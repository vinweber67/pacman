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

    _HUD_HEIGHT = 84
    _DEFAULT_MOVE_INTERVAL = 0.28
    _MIN_PACMAN_BLEND_TIME = 0.12
    _MIN_GHOST_BLEND_TIME = 0.14
    _TELEPORT_SNAP_DISTANCE = 2.5

    def __init__(self) -> None:
        self.state = GameState()
        self._anim_time = 0.0
        self._last_pacman_pos = self.state.pacman_position
        self._pacman_dir = (1, 0)
        self._pacman_visual_pos = (
            float(self.state.pacman_position[0]),
            float(self.state.pacman_position[1]),
        )
        self._ghost_visual_positions: list[tuple[float, float]] = [
            (float(x), float(y)) for x, y in self.state.ghost_positions
        ]

    def on_enter(self) -> None:
        """Prepare gameplay rendering state."""
        return None

    def on_exit(self) -> None:
        """Cleanup gameplay rendering state."""
        return None

    def update(self, delta_time: float) -> None:
        """Update visual animation clocks."""
        safe_delta = max(0.0, delta_time)
        self._anim_time += safe_delta
        self._update_visual_positions(safe_delta)

    @staticmethod
    def _lerp_towards(
        current: tuple[float, float],
        target: tuple[float, float],
        delta_time: float,
        blend_time: float,
    ) -> tuple[float, float]:
        """Move `current` toward `target` using frame-time based smoothing."""
        if blend_time <= 0.0 or delta_time <= 0.0:
            return current

        alpha = min(1.0, delta_time / blend_time)
        nx = current[0] + (target[0] - current[0]) * alpha
        ny = current[1] + (target[1] - current[1]) * alpha

        if abs(nx - target[0]) < 1e-3:
            nx = target[0]
        if abs(ny - target[1]) < 1e-3:
            ny = target[1]
        return nx, ny

    @staticmethod
    def _lerp_towards_grid_aligned(
        current: tuple[float, float],
        target: tuple[float, float],
        delta_time: float,
        blend_time: float,
    ) -> tuple[float, float]:
        """Smooth toward target without diagonal corner cutting.

        If both axes differ, only one axis is advanced for this frame.
        This keeps entities visually centered in maze corridors while turning.
        """
        if blend_time <= 0.0 or delta_time <= 0.0:
            return current

        dx = target[0] - current[0]
        dy = target[1] - current[1]
        if abs(dx) < 1e-6 and abs(dy) < 1e-6:
            return target

        current_x, current_y = current

        # Never blend both axes at once when turning: preserve corridor alignment.
        if abs(dx) > 1e-6 and abs(dy) > 1e-6:
            if abs(dx) >= abs(dy):
                current_y = target[1]
                dy = 0.0
            else:
                current_x = target[0]
                dx = 0.0

        alpha = min(1.0, delta_time / blend_time)
        nx = current_x + dx * alpha
        ny = current_y + dy * alpha

        if abs(nx - target[0]) < 1e-3:
            nx = target[0]
        if abs(ny - target[1]) < 1e-3:
            ny = target[1]
        return nx, ny

    def _update_visual_positions(self, delta_time: float) -> None:
        """Smooth visual positions while keeping gameplay tile-based."""
        move_interval = max(
            0.01,
            float(
                getattr(
                    self.state,
                    "entity_move_interval",
                    self._DEFAULT_MOVE_INTERVAL,
                )
            ),
        )
        pacman_blend_time = max(
            self._MIN_PACMAN_BLEND_TIME,
            move_interval * 0.55,
        )
        ghost_blend_time = max(
            self._MIN_GHOST_BLEND_TIME,
            move_interval * 0.60,
        )

        target_pacman = (
            float(self.state.pacman_position[0]),
            float(self.state.pacman_position[1]),
        )

        if (
            abs(self._pacman_visual_pos[0] - target_pacman[0])
            + abs(self._pacman_visual_pos[1] - target_pacman[1])
            > self._TELEPORT_SNAP_DISTANCE
        ):
            self._pacman_visual_pos = target_pacman
        else:
            self._pacman_visual_pos = self._lerp_towards_grid_aligned(
                self._pacman_visual_pos,
                target_pacman,
                delta_time,
                pacman_blend_time,
            )

        target_ghosts = [
            (float(x), float(y)) for x, y in self.state.ghost_positions
        ]
        if len(self._ghost_visual_positions) != len(target_ghosts):
            self._ghost_visual_positions = target_ghosts
            return

        updated: list[tuple[float, float]] = []
        for current, target in zip(self._ghost_visual_positions, target_ghosts):
            if (
                abs(current[0] - target[0]) + abs(current[1] - target[1])
                > self._TELEPORT_SNAP_DISTANCE
            ):
                updated.append(target)
                continue
            updated.append(
                self._lerp_towards_grid_aligned(
                    current,
                    target,
                    delta_time,
                    ghost_blend_time,
                )
            )
        self._ghost_visual_positions = updated

    @staticmethod
    def _layout(renderer: Renderer, maze: Maze) -> tuple[int, int, int]:
        """Compute dynamic maze layout on screen."""
        horizontal_padding = 12
        top_hud_height = GameScene._HUD_HEIGHT
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

        for index in range(36):
            x = (index * 97 + 23) % max(1, renderer.width)
            y = (index * 53 + 17) % max(1, renderer.height)
            twinkle = 0.35 + 0.65 * (
                (math.sin(self._anim_time * 1.8 + index * 0.9) + 1.0) / 2.0
            )
            brightness = int(90 + 120 * twinkle)
            renderer.draw_circle(x, y, 1, (brightness, brightness, min(255, brightness + 25)))

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
            and any(mask != 0 for row in maze.wall_mask for mask in row)
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
        pacman_x, pacman_y = self._pacman_visual_pos
        cx = int(offset_x + pacman_x * tile_size + tile_size / 2)
        cy = int(offset_y + pacman_y * tile_size + tile_size / 2)
        radius = max(4, tile_size // 2 - 1)

        if self.state.super_mode_time_remaining > 0.0:
            glow_pulse = (math.sin(self._anim_time * 11.0) + 1.0) / 2.0
            glow_radius = radius + 3 + int(glow_pulse * max(2, tile_size // 8))
            renderer.draw_circle(cx, cy, glow_radius + 3, (55, 95, 180))
            renderer.draw_circle(cx, cy, glow_radius, (95, 150, 255))

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
        frightened_blue = (40, 90, 255)
        frightened_white = (240, 240, 255)
        ghost_positions = self._ghost_visual_positions
        if len(ghost_positions) != len(self.state.ghost_positions):
            ghost_positions = [
                (float(x), float(y)) for x, y in self.state.ghost_positions
            ]

        for index, (ghost_x, ghost_y) in enumerate(ghost_positions):
            gx = int(offset_x + ghost_x * tile_size)
            bob_offset = int(
                math.sin(self._anim_time * 5.5 + index * 0.8)
                * max(1, tile_size // 14)
            )
            gy = int(offset_y + ghost_y * tile_size) + bob_offset
            color = ghost_colors[index % len(ghost_colors)]
            is_edible = (
                index < len(self.state.ghost_edible_states)
                and self.state.ghost_edible_states[index]
            )
            if is_edible:
                is_flashing = (
                    self.state.super_mode_time_remaining <= 3.0
                    and int(self._anim_time * 8) % 2 == 0
                )
                color = frightened_white if is_flashing else frightened_blue

            radius = max(4, tile_size // 2)
            center_x = gx + tile_size // 2
            center_y = gy + max(3, tile_size // 2 - 1)

            renderer.draw_circle(
                center_x,
                gy + tile_size - max(2, tile_size // 8),
                max(2, tile_size // 3),
                (14, 16, 28),
            )

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
            pupil_color = (200, 40, 40) if is_edible else (20, 40, 180)
            renderer.draw_circle(left_eye_x + 1, eye_y, pupil_r, pupil_color)
            renderer.draw_circle(
                right_eye_x + 1,
                eye_y,
                pupil_r,
                pupil_color,
            )

        for index, (ghost_x, ghost_y) in enumerate(self.state.ghost_respawn_positions):
            gx = offset_x + ghost_x * tile_size
            gy = offset_y + ghost_y * tile_size
            bob_offset = int(
                math.sin(self._anim_time * 6.5 + index * 1.2)
                * max(1, tile_size // 16)
            )
            eye_y = gy + max(3, tile_size // 2) + bob_offset
            left_eye_x = gx + tile_size // 3
            right_eye_x = gx + (2 * tile_size) // 3
            eye_r = max(2, tile_size // 6)
            pupil_r = max(1, eye_r // 2)

            renderer.draw_circle(
                gx + tile_size // 2,
                gy + tile_size - max(2, tile_size // 8),
                max(2, tile_size // 4),
                (14, 16, 28),
            )
            renderer.draw_circle(left_eye_x, eye_y, eye_r, (255, 255, 255))
            renderer.draw_circle(right_eye_x, eye_y, eye_r, (255, 255, 255))
            renderer.draw_circle(left_eye_x + 1, eye_y, pupil_r, (80, 150, 255))
            renderer.draw_circle(right_eye_x + 1, eye_y, pupil_r, (80, 150, 255))

    def _draw_path_overlay(
        self,
        renderer: Renderer,
        offset_x: int,
        offset_y: int,
        tile_size: int,
    ) -> None:
        """Draw ghost path overlays when the cheat is enabled."""
        if not self.state.show_all_paths:
            return

        path_colors = [
            (255, 90, 90),
            (255, 180, 235),
            (140, 255, 255),
            (255, 205, 120),
        ]
        for index, path in enumerate(self.state.ghost_path_overlays):
            if len(path) < 2:
                continue
            color = path_colors[index % len(path_colors)]
            for start, end in zip(path, path[1:]):
                x1 = offset_x + start[0] * tile_size + tile_size // 2
                y1 = offset_y + start[1] * tile_size + tile_size // 2
                x2 = offset_x + end[0] * tile_size + tile_size // 2
                y2 = offset_y + end[1] * tile_size + tile_size // 2
                renderer.draw_line(x1, y1, x2, y2, color, max(1, tile_size // 10))
                renderer.draw_circle(x2, y2, max(2, tile_size // 9), color)

    def _draw_cheat_overlay(self, renderer: Renderer) -> None:
        """Draw an unobtrusive cheat help panel with current states."""
        if not self.state.cheat_overlay_visible:
            return

        panel_x = max(0, renderer.width - 308)
        panel_y = GameScene._HUD_HEIGHT + 10
        panel_width = 296
        panel_height = 144
        renderer.draw_rect(panel_x, panel_y, panel_width, panel_height, (16, 18, 30))
        renderer.draw_line(
            panel_x,
            panel_y,
            panel_x + panel_width,
            panel_y,
            (110, 170, 255),
            2,
        )
        renderer.draw_text(panel_x + 10, panel_y + 8, "CHEATS (H hide)", (220, 235, 255))

        states = [
            f"I Invincible: {'ON' if self.state.is_invincible else 'OFF'}",
            f"G Freeze: {'ON' if self.state.are_ghosts_frozen else 'OFF'}",
            f"T NoTimer: {'ON' if self.state.no_time_limit else 'OFF'}",
            f"V Paths: {'ON' if self.state.show_all_paths else 'OFF'}",
            f"L +Life  K Speed x{self.state.player_speed_multiplier:.1f}",
            "C Skip level",
        ]
        for index, text in enumerate(states):
            renderer.draw_text(
                panel_x + 10,
                panel_y + 30 + index * 18,
                text,
                (185, 195, 220),
            )

    def _draw_life_icons(self, renderer: Renderer) -> None:
        """Draw compact Pac-Man life icons in the HUD."""
        icon_count = max(0, min(5, int(self.state.lives)))
        spacing = 22
        total_width = max(0, (icon_count - 1) * spacing)
        start_x = renderer.width - total_width - 28
        center_y = 20
        radius = 7

        for index in range(icon_count):
            cx = start_x + index * 22
            renderer.draw_circle(cx, center_y, radius, (255, 215, 40))
            renderer.draw_polygon(
                [
                    (cx + radius + 1, center_y),
                    (cx + radius // 2, center_y - radius // 2),
                    (cx + radius // 2, center_y + radius // 2),
                ],
                (12, 14, 24),
            )

    def _draw_power_meter(self, renderer: Renderer) -> None:
        """Draw a compact power bar when super mode is active."""
        if self.state.super_mode_time_remaining <= 0.0:
            return

        meter_width = 150
        meter_height = 10
        meter_x = renderer.width - meter_width - 160
        meter_y = 36
        ratio = min(1.0, self.state.super_mode_time_remaining / 10.0)
        fill_width = max(0, int(meter_width * ratio))
        pulse = (math.sin(self._anim_time * 10.0) + 1.0) / 2.0
        fill_color = (
            int(90 + 80 * pulse),
            int(150 + 60 * pulse),
            255,
        )

        renderer.draw_rect(meter_x, meter_y, meter_width, meter_height, (22, 28, 44))
        renderer.draw_rect(meter_x, meter_y, fill_width, meter_height, fill_color)
        renderer.draw_line(
            meter_x,
            meter_y - 1,
            meter_x + meter_width,
            meter_y - 1,
            (180, 220, 255),
            1,
        )

    def _draw_progress_text(self, renderer: Renderer) -> None:
        """Draw level progression details in the HUD."""
        progress_text = (
            f"Progress: {self.state.pellets_eaten}/{self.state.pellets_total}"
            " pellets"
        )
        renderer.draw_text(12, 32, progress_text, (205, 218, 255))

        remaining = max(0, self.state.pellets_total - self.state.pellets_eaten)
        renderer.draw_text(
            250,
            32,
            f"Remaining: {remaining}",
            (165, 185, 225),
        )

    def _draw_hud(self, renderer: Renderer) -> None:
        """Draw top HUD with panel background."""
        renderer.draw_rect(0, 0, renderer.width, self._HUD_HEIGHT, (12, 14, 24))
        renderer.draw_line(
            0,
            self._HUD_HEIGHT,
            renderer.width,
            self._HUD_HEIGHT,
            (40, 80, 160),
            2,
        )

        hud_text = (
            f"Score: {self.state.score}    "
            f"Lives: {self.state.lives}    "
            f"Level: {self.state.current_level}    "
            f"Time: {self.state.level_time_remaining}"
        )
        renderer.draw_text(12, 8, hud_text, (240, 240, 255))
        self._draw_progress_text(renderer)
        if self.state.super_mode_time_remaining > 0.0:
            renderer.draw_text(
                renderer.width - 300,
                8,
                (
                    "POWER: "
                    f"{self.state.super_mode_time_remaining:.1f}s"
                ),
                (150, 220, 255),
            )
        self._draw_power_meter(renderer)
        self._draw_life_icons(renderer)
        renderer.draw_text(
            12,
            56,
            "Move: WASD/Arrows | Pause: P | Cheats: H/I/G/L/K/C/T/V | Quit: Q/ESC",
            (170, 178, 205),
        )

    def render(self, renderer: Renderer) -> None:
        """Render maze, entities and HUD with improved details."""
        renderer.clear((8, 10, 20))
        self._draw_background(renderer)

        maze = self.state.maze
        offset_x = 0
        offset_y = self._HUD_HEIGHT
        tile_size = TILE_SIZE

        if maze is not None:
            offset_x, offset_y, tile_size = self._layout(renderer, maze)
            self._draw_maze(renderer, offset_x, offset_y, tile_size)

        self._draw_pellets(renderer, offset_x, offset_y, tile_size)
        self._draw_path_overlay(renderer, offset_x, offset_y, tile_size)
        self._draw_pacman(renderer, offset_x, offset_y, tile_size)
        self._draw_ghosts(renderer, offset_x, offset_y, tile_size)
        self._draw_hud(renderer)
        self._draw_cheat_overlay(renderer)

    def handle_input(self, key: int) -> None:
        """Gameplay input placeholder."""
        del key
