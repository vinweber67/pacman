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
    _TELEPORT_SNAP_DISTANCE = 2.5

    # Speed ratios mirroring the arcade originals (same as GameManager).
    # Visual position advances at exactly these fractions of Pac-Man speed.
    _GHOST_NORMAL_SPEED_RATIO: float = 75.0 / 80.0
    _GHOST_FRIGHTENED_SPEED_RATIO: float = 50.0 / 80.0
    _PELLET_TOUCH_DISTANCE: float = 0.22
    _PELLET_HOLD_MAX_SEC: float = 0.35
    _WIN_PATTERN: tuple[str, ...] = (
        "10001 111 10001",
        "10001 010 11001",
        "10001 010 10101",
        "10101 010 10011",
        "10101 010 10001",
        "11011 010 10001",
        "10001 111 10001",
    )

    # Fraction of the tile occupied by each entity (1.0 = full tile).
    _ENTITY_SCALE: float = 0.70

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
        # Per-ghost queues of logical tile waypoints the visual must visit
        # in order.  Prevents visual shortcuts that cut through walls when
        # the ghost makes a turn before the visual caught up.
        self._ghost_prev_logical: list[tuple[int, int]] = [
            pos for pos in self.state.ghost_positions
        ]
        self._ghost_waypoint_queues: list[list[tuple[int, int]]] = [
            [] for _ in self.state.ghost_positions
        ]
        self._prev_pellet_positions: set[tuple[int, int]] = set(
            self.state.pellet_positions
        )
        self._prev_super_pellet_positions: set[tuple[int, int]] = set(
            self.state.super_pellet_positions
        )
        self._held_eaten_pellets: dict[tuple[int, int], float] = {}
        self._held_eaten_super_pellets: dict[tuple[int, int], float] = {}
        self._maze_draw_cache_key: tuple[int, int, int, int, int, int] | None = None
        self._maze_draw_ops: list[tuple[str, tuple]] = []
        self._power_prev_remaining = 0.0
        self._power_cycle_max = 0.0
        self._power42_maze_id: int = -1
        self._power42_cells: list[tuple[int, int]] = []

    def on_enter(self) -> None:
        """Prepare gameplay rendering state."""
        self._anim_time = 0.0
        self._last_pacman_pos = self.state.pacman_position
        self._pacman_visual_pos = (
            float(self.state.pacman_position[0]),
            float(self.state.pacman_position[1]),
        )
        self._prev_pellet_positions = set(self.state.pellet_positions)
        self._prev_super_pellet_positions = set(self.state.super_pellet_positions)
        self._held_eaten_pellets.clear()
        self._held_eaten_super_pellets.clear()
        self._maze_draw_cache_key = None
        self._maze_draw_ops = []
        self._power_prev_remaining = max(0.0, self.state.super_mode_time_remaining)
        self._power_cycle_max = self._power_prev_remaining
        self._power42_maze_id = -1
        self._power42_cells = []
        return None

    def on_exit(self) -> None:
        """Cleanup gameplay rendering state."""
        return None

    def update(self, delta_time: float) -> None:
        """Update visual animation clocks."""
        safe_delta = max(0.0, delta_time)
        self._anim_time += safe_delta
        self._update_visual_positions(safe_delta)
        self._update_pellet_visual_hold(safe_delta)

        current_power = max(0.0, self.state.super_mode_time_remaining)
        if current_power > 0.0 and self._power_prev_remaining <= 0.0:
            self._power_cycle_max = current_power
        elif current_power > 0.0:
            self._power_cycle_max = max(self._power_cycle_max, current_power)
        self._power_prev_remaining = current_power

    def _update_pellet_visual_hold(self, delta_time: float) -> None:
        """Delay pellet disappearance until Pac-Man visually reaches it."""
        current_pellets = set(self.state.pellet_positions)
        current_super = set(self.state.super_pellet_positions)
        pacman_tile = self.state.pacman_position

        for pos in self._prev_pellet_positions - current_pellets:
            if pos == pacman_tile:
                self._held_eaten_pellets[pos] = self._PELLET_HOLD_MAX_SEC

        for pos in self._prev_super_pellet_positions - current_super:
            if pos == pacman_tile:
                self._held_eaten_super_pellets[pos] = self._PELLET_HOLD_MAX_SEC

        visual_x, visual_y = self._pacman_visual_pos

        def _is_visually_touched(position: tuple[int, int]) -> bool:
            return (
                math.hypot(visual_x - position[0], visual_y - position[1])
                <= self._PELLET_TOUCH_DISTANCE
            )

        for position in list(self._held_eaten_pellets.keys()):
            remaining = self._held_eaten_pellets[position] - delta_time
            if _is_visually_touched(position) or remaining <= 0.0:
                del self._held_eaten_pellets[position]
            else:
                self._held_eaten_pellets[position] = remaining

        for position in list(self._held_eaten_super_pellets.keys()):
            remaining = self._held_eaten_super_pellets[position] - delta_time
            if _is_visually_touched(position) or remaining <= 0.0:
                del self._held_eaten_super_pellets[position]
            else:
                self._held_eaten_super_pellets[position] = remaining

        self._prev_pellet_positions = current_pellets
        self._prev_super_pellet_positions = current_super

    @staticmethod
    def _advance_constant_velocity(
        current: tuple[float, float],
        target: tuple[float, float],
        speed_tps: float,
        delta_time: float,
    ) -> tuple[float, float]:
        """Move `current` toward `target` at a perfectly constant speed.

        `speed_tps` is expressed in tiles-per-second.  The entity travels
        at exactly that speed every frame regardless of frame timing, giving
        smooth, stutter-free motion.

        When both axes differ (corner turn), the axis that is almost aligned
        is snapped first so the entity stays centered in corridors.
        """
        if speed_tps <= 0.0 or delta_time <= 0.0:
            return current

        dx = target[0] - current[0]
        dy = target[1] - current[1]
        if abs(dx) < 1e-6 and abs(dy) < 1e-6:
            return target

        cur_x, cur_y = current

        # Grid-aligned: snap the nearly-aligned axis first when turning.
        if abs(dx) > 1e-6 and abs(dy) > 1e-6:
            if abs(dx) >= abs(dy):
                cur_y = target[1]
                dy = 0.0
            else:
                cur_x = target[0]
                dx = 0.0

        dist = abs(dx) + abs(dy)
        step = speed_tps * delta_time
        if step >= dist:
            return target

        ratio = step / dist
        return (cur_x + dx * ratio, cur_y + dy * ratio)

    def _update_visual_positions(self, delta_time: float) -> None:
        """Advance visual positions at constant velocity toward logical targets.

        Each entity moves at exactly `1 tile / move_interval` tiles per second
        so the visual always travels at constant speed between tile steps,
        giving perfectly smooth motion independent of frame timing.
        """
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
        # Pac-Man: 1 tile every move_interval seconds.
        pacman_speed = 1.0 / move_interval

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
            self._pacman_visual_pos = self._advance_constant_velocity(
                self._pacman_visual_pos,
                target_pacman,
                pacman_speed,
                delta_time,
            )

        target_ghosts = [
            (x, y) for x, y in self.state.ghost_positions
        ]
        n = len(target_ghosts)

        # Resize state lists when ghost count changes.
        if len(self._ghost_visual_positions) != n:
            self._ghost_visual_positions = [
                (float(x), float(y)) for x, y in target_ghosts
            ]
            self._ghost_prev_logical = list(target_ghosts)
            self._ghost_waypoint_queues = [[] for _ in target_ghosts]
            return

        updated: list[tuple[float, float]] = []
        for i, logical in enumerate(target_ghosts):
            prev = self._ghost_prev_logical[i]
            queue = self._ghost_waypoint_queues[i]

            # Detect a new logical step and enqueue it.
            if logical != prev:
                dist = abs(logical[0] - prev[0]) + abs(logical[1] - prev[1])
                if float(dist) <= self._TELEPORT_SNAP_DISTANCE:
                    queue.append(logical)
                else:
                    # Teleport: flush queue, snap visual immediately.
                    queue.clear()
                    self._ghost_visual_positions[i] = (
                        float(logical[0]),
                        float(logical[1]),
                    )
                self._ghost_prev_logical[i] = logical

            current = self._ghost_visual_positions[i]

            # Drain waypoints at constant velocity, tile by tile.
            is_edible = (
                i < len(self.state.ghost_edible_states)
                and self.state.ghost_edible_states[i]
            )
            speed_ratio = (
                self._GHOST_FRIGHTENED_SPEED_RATIO
                if is_edible
                else self._GHOST_NORMAL_SPEED_RATIO
            )
            ghost_speed = speed_ratio / move_interval
            remaining_dt = delta_time

            while queue and remaining_dt > 0.0:
                wp = (float(queue[0][0]), float(queue[0][1]))
                dx = wp[0] - current[0]
                dy = wp[1] - current[1]
                seg_dist = abs(dx) + abs(dy)
                if seg_dist < 1e-6:
                    queue.pop(0)
                    current = wp
                    continue
                step = ghost_speed * remaining_dt
                if step >= seg_dist:
                    remaining_dt -= seg_dist / ghost_speed
                    current = wp
                    queue.pop(0)
                else:
                    ratio = step / seg_dist
                    current = (
                        current[0] + dx * ratio,
                        current[1] + dy * ratio,
                    )
                    remaining_dt = 0.0

            updated.append(current)
        self._ghost_visual_positions = updated

        # Publish sub-tile positions so GameManager can do pixel-accurate
        # collision detection instead of tile-exact comparisons.
        self.state.set_pacman_visual_pos(
            self._pacman_visual_pos[0], self._pacman_visual_pos[1]
        )
        self.state.set_ghost_visual_positions_float(self._ghost_visual_positions)

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
        thickness = max(2, tile_size // 9)
        highlight = max(1, thickness // 3)
        radius = max(1, thickness // 2)
        cache_key = (
            id(maze),
            maze.width,
            maze.height,
            offset_x,
            offset_y,
            tile_size,
        )

        if self._maze_draw_cache_key != cache_key:
            draw_ops: list[tuple[str, tuple]] = []

            def _add_rect(
                x: int,
                y: int,
                width: int,
                height: int,
                color: tuple[int, int, int],
            ) -> None:
                draw_ops.append(("rect", (x, y, width, height, color)))

            def _add_line(
                x1: int,
                y1: int,
                x2: int,
                y2: int,
                color: tuple[int, int, int],
                width: int,
            ) -> None:
                draw_ops.append(("line", (x1, y1, x2, y2, color, width)))

            def _add_circle(
                x: int,
                y: int,
                circle_radius: int,
                color: tuple[int, int, int],
            ) -> None:
                draw_ops.append(("circle", (x, y, circle_radius, color)))

            def _draw_round_node(cx: int, cy: int) -> None:
                _add_circle(cx, cy, radius, wall_color)
                _add_circle(cx - 1, cy - 1, max(1, highlight), wall_glow)
                _add_circle(cx + 1, cy + 1, max(1, highlight), wall_shadow)

            def _draw_horizontal_wall(px: int, py: int) -> None:
                cy = py + radius
                x1 = px
                x2 = px + tile_size - 1
                _add_line(x1, cy, x2, cy, wall_color, thickness)
                _add_line(
                    x1,
                    max(py, cy - radius + highlight),
                    x2,
                    max(py, cy - radius + highlight),
                    wall_glow,
                    highlight,
                )
                _add_line(
                    x1,
                    min(py + thickness - 1, cy + radius - highlight),
                    x2,
                    min(py + thickness - 1, cy + radius - highlight),
                    wall_shadow,
                    highlight,
                )
                _draw_round_node(x1, cy)
                _draw_round_node(x2, cy)

            def _draw_vertical_wall(px: int, py: int) -> None:
                cx = px + radius
                y1 = py
                y2 = py + tile_size - 1
                _add_line(cx, y1, cx, y2, wall_color, thickness)
                _add_line(
                    max(px, cx - radius + highlight),
                    y1,
                    max(px, cx - radius + highlight),
                    y2,
                    wall_glow,
                    highlight,
                )
                _add_line(
                    min(px + thickness - 1, cx + radius - highlight),
                    y1,
                    min(px + thickness - 1, cx + radius - highlight),
                    y2,
                    wall_shadow,
                    highlight,
                )
                _draw_round_node(cx, y1)
                _draw_round_node(cx, y2)

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
                    _add_rect(px, py, tile_size, tile_size, floor_color)

                    if has_wall_mask:
                        mask = maze.wall_mask[y][x]
                        # Draw each shared edge once (canonical sides):
                        # - horizontal walls from top edges
                        # - vertical walls from left edges
                        if mask & 1:
                            _draw_horizontal_wall(px, py)

                        if mask & 8:
                            _draw_vertical_wall(px, py)

                        # Keep outer frame closed on right/bottom boundaries.
                        if x == maze.width - 1 and (mask & 2):
                            _draw_vertical_wall(px + tile_size - thickness, py)
                        if y == maze.height - 1 and (mask & 4):
                            _draw_horizontal_wall(px, py + tile_size - thickness)
                    elif maze.tiles[y][x] == TileType.WALL:
                        _add_rect(
                            px,
                            py,
                            tile_size,
                            tile_size,
                            (10, 35, 160),
                        )

            # Blend wall junctions so corners / T-junctions look cleaner.
            if has_wall_mask:
                for y in range(maze.height + 1):
                    for x in range(maze.width + 1):
                        has_horizontal = False
                        has_vertical = False

                        # Horizontal segment touching this vertex.
                        if y < maze.height:
                            if x < maze.width and (maze.wall_mask[y][x] & 1):
                                has_horizontal = True
                            elif x > 0 and (maze.wall_mask[y][x - 1] & 1):
                                has_horizontal = True
                        elif (
                            y > 0
                            and x < maze.width
                            and (maze.wall_mask[y - 1][x] & 4)
                        ):
                            has_horizontal = True

                        # Vertical segment touching this vertex.
                        if x < maze.width:
                            if y < maze.height and (maze.wall_mask[y][x] & 8):
                                has_vertical = True
                            elif y > 0 and (maze.wall_mask[y - 1][x] & 8):
                                has_vertical = True
                        elif (
                            x > 0
                            and y < maze.height
                            and (maze.wall_mask[y][x - 1] & 2)
                        ):
                            has_vertical = True

                        if not (has_horizontal and has_vertical):
                            continue

                        vx = offset_x + x * tile_size
                        vy = offset_y + y * tile_size
                        join_x = vx + (radius if x < maze.width else -radius)
                        join_y = vy + (radius if y < maze.height else -radius)
                        _draw_round_node(join_x, join_y)

            self._maze_draw_cache_key = cache_key
            self._maze_draw_ops = draw_ops

        for op, params in self._maze_draw_ops:
            if op == "rect":
                x, y, width, height, color = params
                renderer.draw_rect(x, y, width, height, color)
                continue
            if op == "line":
                x1, y1, x2, y2, color, width = params
                renderer.draw_line(x1, y1, x2, y2, color, width)
                continue
            x, y, circle_radius, color = params
            renderer.draw_circle(x, y, circle_radius, color)

    def _draw_pellets(
        self,
        renderer: Renderer,
        offset_x: int,
        offset_y: int,
        tile_size: int,
    ) -> None:
        """Draw classic pellets and animated super pellets."""
        visible_pellets = set(self.state.pellet_positions)
        visible_pellets.update(self._held_eaten_pellets.keys())
        for pellet_x, pellet_y in visible_pellets:
            cx = offset_x + pellet_x * tile_size + tile_size // 2
            cy = offset_y + pellet_y * tile_size + tile_size // 2
            radius = max(2, tile_size // 8)
            renderer.draw_circle(cx, cy, radius + 1, (255, 245, 190))
            renderer.draw_circle(cx, cy, radius, (255, 230, 130))

        pulse = (math.sin(self._anim_time * 6.0) + 1.0) / 2.0
        visible_super = set(self.state.super_pellet_positions)
        visible_super.update(self._held_eaten_super_pellets.keys())
        for pellet_x, pellet_y in visible_super:
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
        radius = max(3, int(tile_size * self._ENTITY_SCALE / 2))

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

        openness = 0.16 + 0.24 * abs(math.sin(self._anim_time * 18.0))
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

            radius = max(3, int(tile_size * self._ENTITY_SCALE / 2))
            half = tile_size // 2
            body_w = int(tile_size * self._ENTITY_SCALE)
            body_x = gx + (tile_size - body_w) // 2
            center_x = gx + half
            center_y = gy + half

            renderer.draw_circle(center_x, center_y, radius, color)
            renderer.draw_rect(
                body_x,
                gy + half,
                body_w,
                radius,
                color,
            )

            eye_y = gy + half - radius // 4
            eye_offset = max(2, radius // 3)
            left_eye_x = center_x - eye_offset
            right_eye_x = center_x + eye_offset
            eye_r = max(1, radius // 3)
            pupil_r = max(1, eye_r // 2)
            renderer.draw_circle(left_eye_x, eye_y, eye_r, (255, 255, 255))
            renderer.draw_circle(right_eye_x, eye_y, eye_r, (255, 255, 255))
            pupil_color = (200, 40, 40) if is_edible else (20, 40, 180)
            renderer.draw_circle(left_eye_x, eye_y, pupil_r, pupil_color)
            renderer.draw_circle(
                right_eye_x,
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
            eye_y = gy + tile_size // 2 + bob_offset
            radius_r = max(3, int(tile_size * self._ENTITY_SCALE / 2))
            eye_offset = max(2, radius_r // 3)
            left_eye_x = gx + tile_size // 2 - eye_offset
            right_eye_x = gx + tile_size // 2 + eye_offset
            eye_r = max(1, radius_r // 3)
            pupil_r = max(1, eye_r // 2)

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

    def _draw_win_pellet_stack(
        self,
        renderer: Renderer,
        maze: Maze,
        offset_x: int,
        offset_y: int,
        tile_size: int,
    ) -> None:
        """Stack collected pellets on the side to progressively draw WIN."""
        pattern = self._WIN_PATTERN
        rows = len(pattern)
        cols = len(pattern[0]) if rows > 0 else 0
        if rows == 0 or cols == 0:
            return

        # Bigger by default, but always fit the viewport.
        desired_cell = max(8, min(20, tile_size))

        maze_left = offset_x
        maze_top = offset_y
        maze_w = maze.width * tile_size
        maze_h = maze.height * tile_size
        maze_right = maze_left + maze_w
        maze_bottom = maze_top + maze_h

        # Compute a visible size first (independent from outside-zone size).
        fit_cell = min(
            desired_cell,
            max(4, (renderer.width - 20) // max(1, cols)),
            max(4, (renderer.height - self._HUD_HEIGHT - 20) // max(1, rows)),
        )

        cell = max(4, fit_cell)
        gap = max(1, cell // 6)
        pattern_w = cols * cell
        pattern_h = rows * cell

        # Anchor at midpoint between maze BR corner and screen BR corner.
        anchor_x = (maze_right + renderer.width) // 2
        anchor_y = (maze_bottom + renderer.height) // 2

        x = anchor_x - pattern_w // 2
        y = anchor_y - pattern_h // 2

        # Preferred outside bounds (bottom-right of maze).
        min_outside_x = maze_right + 10
        min_outside_y = maze_bottom + 10
        max_x = renderer.width - pattern_w - 8
        max_y = renderer.height - pattern_h - 8

        # Try to keep it in the requested outside area first.
        if min_outside_x <= max_x:
            x = max(min_outside_x, min(x, max_x))
        else:
            x = max(8, min(x, max_x))

        if min_outside_y <= max_y:
            y = max(min_outside_y, min(y, max_y))
        else:
            y = max(self._HUD_HEIGHT + 8, min(y, max_y))

        # Guarantee the pattern is outside maze even when bottom space is tiny:
        # right of maze OR below maze.
        if x < min_outside_x and y < min_outside_y:
            if min_outside_x <= max_x:
                x = min_outside_x
            elif min_outside_y <= max_y:
                y = min_outside_y

        # Detect letter column ranges from the pattern (W, I, N).
        # Spaces in the pattern separate letters.
        letter_ranges: list[tuple[int, int]] = []
        in_segment = False
        seg_start = 0
        for col, ch in enumerate(pattern[0]):
            if ch != " " and not in_segment:
                in_segment = True
                seg_start = col
            elif ch == " " and in_segment:
                in_segment = False
                letter_ranges.append((seg_start, col - 1))
        if in_segment:
            letter_ranges.append((seg_start, len(pattern[0]) - 1))

        def _letter_index(col: int) -> int:
            for idx, (start, end) in enumerate(letter_ranges):
                if start <= col <= end:
                    return idx
            return len(letter_ranges)

        # Gather slot coordinates where a pellet can be stacked.
        # Tuple shape: (letter_index, px, py)
        slots: list[tuple[int, int, int]] = []
        for r, line in enumerate(pattern):
            for c, bit in enumerate(line):
                if bit != "1":
                    continue
                px = x + c * cell
                py = y + r * cell
                slots.append((_letter_index(c), px, py))

        if not slots:
            return

        # Fill order: W first, then I, then N.
        # Inside each letter: bottom to top, then left to right.
        fill_order = sorted(slots, key=lambda pos: (pos[0], -pos[2], pos[1]))
        pellets_total = max(0, int(self.state.pellets_total))
        pellets_eaten = max(0, int(self.state.pellets_eaten))
        if pellets_total <= 0:
            filled = 0
        else:
            progress = max(0.0, min(1.0, pellets_eaten / pellets_total))
            filled = int(round(len(fill_order) * progress))

        # Subtle panel for readability.
        panel_pad = 6
        renderer.draw_rect(
            x - panel_pad,
            y - panel_pad,
            pattern_w + panel_pad * 2,
            pattern_h + panel_pad * 2,
            (12, 18, 34),
        )

        pulse = (math.sin(self._anim_time * 10.0) + 1.0) / 2.0
        lit_color = (255, int(210 + 40 * pulse), 90)
        dim_color = (26, 42, 76)

        for index, (_, px, py) in enumerate(fill_order):
            color = lit_color if index < filled else dim_color
            renderer.draw_rect(px + gap, py + gap, cell - 2 * gap, cell - 2 * gap, color)

    def _get_power42_cells(self, maze: Maze) -> list[tuple[int, int]]:
        """Return the WALL cells that form the '42' shape baked into the maze.

        The wheel generator embeds a '42' by adding fully-walled cells
        (wall_mask == 15, TileType.WALL) in the centre of the maze.
        We isolate them by flood-filling the reachable wall mass from every
        border cell and keeping the wall cells NOT reachable from the border
        (i.e. the interior '42' block that floats in the middle).
        """
        mid = id(maze)
        if mid == self._power42_maze_id:
            return self._power42_cells

        self._power42_maze_id = mid

        # Collect all fully-walled (solid) cells.
        all_walls: set[tuple[int, int]] = set()
        for gy in range(maze.height):
            for gx in range(maze.width):
                if maze.wall_mask[gy][gx] == 15:
                    all_walls.add((gx, gy))

        # Flood-fill from border solid cells to find walls touching the border.
        border_walls: set[tuple[int, int]] = set()
        stack: list[tuple[int, int]] = []
        for pos in all_walls:
            gx, gy = pos
            if gx == 0 or gy == 0 or gx == maze.width - 1 or gy == maze.height - 1:
                stack.append(pos)

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        while stack:
            pos = stack.pop()
            if pos in border_walls:
                continue
            border_walls.add(pos)
            cx, cy = pos
            for dx, dy in directions:
                nb = (cx + dx, cy + dy)
                if nb in all_walls and nb not in border_walls:
                    stack.append(nb)

        # Interior '42' cells = solid walls NOT connected to the border mass.
        interior = sorted(
            all_walls - border_walls,
            key=lambda c: (c[1], c[0]),
        )
        self._power42_cells = interior
        return interior

    def _draw_center_power_42(
        self,
        renderer: Renderer,
        offset_x: int,
        offset_y: int,
        tile_size: int,
    ) -> None:
        """Fill the enclosed '42' wall cells as a draining power gauge."""
        maze = self.state.maze
        remaining = max(0.0, self.state.super_mode_time_remaining)
        if maze is None or remaining <= 0.0:
            return

        cells = self._get_power42_cells(maze)
        if not cells:
            return

        cycle_max = max(remaining, self._power_cycle_max, 0.001)
        ratio = max(0.0, min(1.0, remaining / cycle_max))

        # Split cells into "4" (left half) and "2" (right half) by x-midpoint.
        mid_x = (min(gx for gx, _ in cells) + max(gx for gx, _ in cells)) / 2.0
        cells_4 = sorted(
            [(gx, gy) for gx, gy in cells if gx <= mid_x],
            key=lambda c: (c[1], c[0]),
        )
        cells_2 = sorted(
            [(gx, gy) for gx, gy in cells if gx > mid_x],
            key=lambda c: (c[1], c[0]),
        )

        # For cells_2, follow the "2" curve: top→right, middle→left, bottom→right.
        # Split "2" vertically into thirds.
        if cells_2:
            min_y2 = min(gy for _, gy in cells_2)
            max_y2 = max(gy for _, gy in cells_2)
            y_range = max(1, max_y2 - min_y2)
            third_h = y_range / 3.0

            def sort_key_2(cell: tuple[int, int]) -> tuple:
                gx, gy = cell
                rel_y = gy - min_y2
                if rel_y < third_h:
                    # Top third: left to right
                    return (0, rel_y, gx)
                elif rel_y < 2 * third_h:
                    # Middle third: right to left (negate gx)
                    return (1, rel_y, -gx)
                else:
                    # Bottom third: left to right
                    return (2, rel_y, gx)

            cells_2 = sorted(cells_2, key=sort_key_2)

        # Drain order: "4" first (top→bottom), then "2" (following curve).
        ordered = cells_4 + cells_2
        total = len(ordered)
        # fill_count = cells still lit (from the end of ordered list).
        fill_count = max(0, int(math.ceil(total * ratio)))

        # Index boundary: cells_2 starts at len(cells_4) in ordered.
        len4 = len(cells_4)
        len2 = len(cells_2)
        # "2" half-drain threshold (in ordered index).
        half_2_start = len4 + len2 // 2

        # The drain front index: first cell that is still lit.
        drain_front = total - fill_count
        # Urgent mode activates only once the drain front has entered the
        # second half of the "2" — i.e. we are actually draining those cells.
        urgent_mode = drain_front >= half_2_start

        empty_color = (20, 35, 80)
        pad = 0
        sz = tile_size

        for i, (gx, gy) in enumerate(ordered):
            px = offset_x + gx * tile_size
            py = offset_y + gy * tile_size
            lit = i >= drain_front
            if not lit:
                renderer.draw_rect(px, py, sz, sz, empty_color)
                continue

            # Urgency: only blink red once the drain front has reached those cells.
            in_urgent_zone = urgent_mode and i >= half_2_start
            if in_urgent_zone:
                blink = math.sin(self._anim_time * 14.0)
                if blink > 0.0:
                    pulse = (blink + 1.0) / 2.0
                    fill_color = (
                        int(200 + 55 * pulse),
                        int(20 * (1.0 - pulse)),
                        int(20 * (1.0 - pulse)),
                    )
                else:
                    fill_color = empty_color
            else:
                pulse = (math.sin(self._anim_time * 8.0) + 1.0) / 2.0
                fill_color = (
                    int(70 + 110 * pulse),
                    int(175 + 65 * pulse),
                    255,
                )
            renderer.draw_rect(px, py, sz, sz, fill_color)

    def _draw_power42_walls(
        self,
        renderer: Renderer,
        offset_x: int,
        offset_y: int,
        tile_size: int,
    ) -> None:
        """Redraw the walls of the '42' cells on top of the colored fill, matching _draw_maze style."""
        maze = self.state.maze
        if maze is None or self.state.super_mode_time_remaining <= 0.0:
            return

        cells = self._get_power42_cells(maze)
        if not cells:
            return

        wall_color = (20, 92, 255)
        wall_glow = (90, 160, 255)
        wall_shadow = (8, 38, 120)
        thickness = max(2, tile_size // 9)
        highlight = max(1, thickness // 3)
        radius = max(1, thickness // 2)

        def _draw_round_node(cx: int, cy: int) -> None:
            renderer.draw_circle(cx, cy, radius, wall_color)
            renderer.draw_circle(cx - 1, cy - 1, max(1, highlight), wall_glow)
            renderer.draw_circle(cx + 1, cy + 1, max(1, highlight), wall_shadow)

        def _draw_horizontal_wall(px: int, py: int) -> None:
            cy = py + radius
            x1 = px
            x2 = px + tile_size - 1
            renderer.draw_line(x1, cy, x2, cy, wall_color, thickness)
            renderer.draw_line(
                x1,
                max(py, cy - radius + highlight),
                x2,
                max(py, cy - radius + highlight),
                wall_glow,
                highlight,
            )
            renderer.draw_line(
                x1,
                min(py + thickness - 1, cy + radius - highlight),
                x2,
                min(py + thickness - 1, cy + radius - highlight),
                wall_shadow,
                highlight,
            )
            _draw_round_node(x1, cy)
            _draw_round_node(x2, cy)

        def _draw_vertical_wall(px: int, py: int) -> None:
            cx = px + radius
            y1 = py
            y2 = py + tile_size - 1
            renderer.draw_line(cx, y1, cx, y2, wall_color, thickness)
            renderer.draw_line(
                max(px, cx - radius + highlight),
                y1,
                max(px, cx - radius + highlight),
                y2,
                wall_glow,
                highlight,
            )
            renderer.draw_line(
                min(px + thickness - 1, cx + radius - highlight),
                y1,
                min(px + thickness - 1, cx + radius - highlight),
                y2,
                wall_shadow,
                highlight,
            )
            _draw_round_node(cx, y1)
            _draw_round_node(cx, y2)

        for gx, gy in cells:
            px = offset_x + gx * tile_size
            py = offset_y + gy * tile_size
            mask = maze.wall_mask[gy][gx]

            # Draw walls for each direction (bits: top=1, right=2, bottom=4, left=8)
            if mask & 1:  # Top wall
                _draw_horizontal_wall(px, py)
            if mask & 8:  # Left wall
                _draw_vertical_wall(px, py)

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
            self._draw_win_pellet_stack(renderer, maze, offset_x, offset_y, tile_size)
            self._draw_center_power_42(renderer, offset_x, offset_y, tile_size)
            self._draw_power42_walls(renderer, offset_x, offset_y, tile_size)

        self._draw_pellets(renderer, offset_x, offset_y, tile_size)
        self._draw_path_overlay(renderer, offset_x, offset_y, tile_size)
        self._draw_pacman(renderer, offset_x, offset_y, tile_size)
        self._draw_ghosts(renderer, offset_x, offset_y, tile_size)
        self._draw_hud(renderer)
        self._draw_cheat_overlay(renderer)

    def handle_input(self, key: int) -> None:
        """Gameplay input placeholder."""
        del key
