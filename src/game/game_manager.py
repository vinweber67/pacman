"""Game manager integration layer."""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.cheat.cheat_mode import CheatMode
from src.entities.ai.ghost_behavior import GhostAI
from src.utils.constants import Direction
from src.input.input_handler import InputHandler
from src.input.key_bindings import Action
from src.game.game_loop import GameLoop
from src.game.game_state import GameState
from src.game.level_manager import LevelData
from src.game.level_manager import LevelManager
from src.highscore.highscore_manager import HighscoreManager
from src.ui.ui_manager import UIManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GameManager:
    """Coordinate level loading, UI and the main loop."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.state = GameState()
        self.ui_manager = UIManager()
        self.level_manager = LevelManager(config)
        self.highscore_manager = HighscoreManager(
            config.get("highscore_filename", ".data/highscores.json")
        )
        self.loop = GameLoop(self)
        self.current_level: LevelData | None = None
        self._ghost_move_accumulator = 0.0

    def start_game(self) -> None:
        """Start a new run from the first level."""
        self.state.reset()
        self.current_level = self.level_manager.load_level(1)
        self.ui_manager.switch_scene("game")
        self.loop.running = True

    def on_level_timeout(self) -> None:
        """Handle a timeout by consuming a life or ending the game."""
        self.state.lose_life()
        if self.state.is_game_over:
            self._show_end_scene("GAME OVER")
            return
        self.current_level = self.level_manager.load_level(
            self.state.current_level,
        )

    def update(self, delta_time: float) -> None:
        """Update the active scene."""
        if self.ui_manager.current_scene_name == "game":
            self._update_gameplay(delta_time)
        self.ui_manager.update(delta_time)

    def _update_gameplay(self, delta_time: float) -> None:
        """Update active gameplay entities and collisions."""
        if self.current_level is None:
            return

        self._update_ghost_path_overlay()

        for ghost in self.current_level.ghosts:
            ghost.update(delta_time)

        self._ghost_move_accumulator += delta_time
        if (
            self._ghost_move_accumulator >= 0.18
            and not self.state.are_ghosts_frozen
        ):
            self._ghost_move_accumulator = 0.0
            self._move_ghosts()

        self._sync_ghost_render_state()
        self._check_ghost_collisions()
        self._sync_ghost_render_state()
        self.state.set_super_mode_time_remaining(
            max(
                (ghost.edible_timer for ghost in self.current_level.ghosts),
                default=0.0,
            )
        )

    def _sync_ghost_render_state(self) -> None:
        """Synchronize ghost render data stored in the shared game state."""
        if self.current_level is None:
            self.state.set_ghost_positions([])
            self.state.set_ghost_edible_states([])
            self.state.set_ghost_respawn_positions([])
            return

        self.state.set_ghost_positions(
            [
                ghost.position
                for ghost in self.current_level.ghosts
                if not ghost.is_respawning
            ]
        )
        self.state.set_ghost_edible_states(
            [
                ghost.is_edible
                for ghost in self.current_level.ghosts
                if not ghost.is_respawning
            ]
        )
        self.state.set_ghost_respawn_positions(
            [
                (ghost.spawn_x, ghost.spawn_y)
                for ghost in self.current_level.ghosts
                if ghost.is_respawning
            ]
        )

    def _update_ghost_path_overlay(self) -> None:
        """Refresh stored ghost paths for the optional cheat overlay."""
        if self.current_level is None or not self.state.show_all_paths:
            self.state.set_ghost_path_overlays([])
            return

        maze = self.current_level.maze
        pacman = self.current_level.pacman
        overlays = [
            GhostAI.calculate_path(ghost, pacman, maze)
            for ghost in self.current_level.ghosts
            if not ghost.is_respawning
        ]
        self.state.set_ghost_path_overlays(
            [path for path in overlays if len(path) >= 2]
        )

    def _move_ghosts(self) -> None:
        """Move each ghost one step according to its behavior."""
        if self.current_level is None:
            return

        maze = self.current_level.maze
        pacman = self.current_level.pacman

        for ghost in self.current_level.ghosts:
            next_tile = GhostAI.calculate_next_move(ghost, pacman, maze)
            if next_tile is None:
                continue
            ghost.move_to(next_tile[0], next_tile[1])

    def _check_ghost_collisions(self) -> None:
        """Resolve collisions between Pac-Man and ghosts."""
        if self.current_level is None:
            return

        pacman = self.current_level.pacman
        for ghost in self.current_level.ghosts:
            if ghost.is_respawning:
                continue
            if ghost.position != pacman.position:
                continue

            if ghost.is_edible:
                self.state.add_score(
                    int(self.config.get("points_per_ghost", 200))
                )
                ghost.start_respawn(
                    float(self.config.get("ghost_respawn_time", 10))
                )
                self._sync_ghost_render_state()
                continue

            if self.state.is_invincible:
                continue

            self.state.lose_life()
            if self.state.is_game_over:
                self._show_end_scene("GAME OVER")
                self._sync_ghost_render_state()
                return

            maze = self.current_level.maze
            center_x, center_y = maze.get_center()
            pacman.move_to(center_x, center_y)
            self.state.set_pacman_position(center_x, center_y)
            self._sync_ghost_render_state()
            return

    def render(self) -> None:
        """Render the active scene."""
        self.ui_manager.render()

    def handle_input(self, key: int) -> None:
        """Handle raw input events."""
        action = InputHandler.key_to_action(key)
        scene_name = self.ui_manager.current_scene_name

        if scene_name == "game_over":
            self.ui_manager.handle_input(key)
            scene = self.ui_manager.current_scene
            consume_name = getattr(scene, "consume_submitted_name", None)
            if callable(consume_name):
                submitted_name = consume_name()
                if submitted_name is not None:
                    self.finish_game(submitted_name)
                    self.ui_manager.switch_scene("menu")
            return

        if key in (27, 65307):
            if scene_name in {"highscores", "instructions", "game_over"}:
                self.ui_manager.switch_scene("menu")
                return
            if scene_name == "pause":
                self.state.resume()
                self.ui_manager.switch_scene("game")
                return
            if scene_name == "game":
                self.state.pause()
                self.ui_manager.switch_scene("pause")
                return

        if key in (ord("q"),):
            self.ui_manager.switch_scene("menu")
            self.loop.stop()
            return

        if action in {
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        }:
            if scene_name == "game":
                self._move_pacman(action)
            else:
                self.ui_manager.handle_input(key)
            return

        if action == Action.PAUSE:
            if scene_name == "game":
                self.state.pause()
                self.ui_manager.switch_scene("pause")
            elif scene_name == "pause":
                self.state.resume()
                self.ui_manager.switch_scene("game")
            return

        if action == Action.SELECT:
            self._handle_select(scene_name)
            return

        if key == ord("c"):
            CheatMode.skip_level(self.state)
            if self.level_manager.has_more_levels():
                self.current_level = self.level_manager.advance_level()
            else:
                self.state.is_victory = True
                self.loop.stop()
            return

        if key == ord("t"):
            CheatMode.toggle_no_time_limit(self.state)
            return

        if key == ord("i"):
            CheatMode.toggle_invincibility(self.state)
            return

        if key == ord("g"):
            CheatMode.freeze_ghosts(self.state)
            return

        if key == ord("l"):
            CheatMode.add_lives(self.state)
            return

        if key == ord("k"):
            CheatMode.increase_speed(self.state)
            return

        if key == ord("v"):
            CheatMode.toggle_show_all_paths(self.state)
            self._update_ghost_path_overlay()
            return

        if key == ord("h"):
            CheatMode.toggle_overlay(self.state)
            return

        self.ui_manager.handle_input(key)

    def _handle_select(self, scene_name: str) -> None:
        """Handle selection action depending on active scene."""
        if scene_name == "menu":
            menu_scene = self.ui_manager.current_scene
            selected = getattr(menu_scene, "selected", 0)
            options = getattr(menu_scene, "options", [])
            if not options or selected >= len(options):
                return

            selected_option = options[selected]
            if selected_option == "Start Game":
                self.start_game()
            elif selected_option in {"Highscores", "View Highscores"}:
                self._open_highscores()
            elif selected_option == "Instructions":
                self.ui_manager.switch_scene("instructions")
            elif selected_option == "Exit":
                self.loop.stop()
            return

        if scene_name == "pause":
            pause_scene = self.ui_manager.current_scene
            selected = getattr(pause_scene, "selected", 0)
            options = getattr(pause_scene, "options", [])
            if not options or selected >= len(options):
                return

            selected_option = options[selected]
            if selected_option == "Resume":
                self.state.resume()
                self.ui_manager.switch_scene("game")
            elif selected_option == "Main Menu":
                self.state.resume()
                self.ui_manager.switch_scene("menu")

    def _open_highscores(self) -> None:
        """Prepare and open highscores scene."""
        top_scores = self.highscore_manager.get_top_10()
        rows: list[str] = []
        for index, entry in enumerate(top_scores, start=1):
            rows.append(f"{index:02d}  {entry.name:<10}  {entry.score}")
        self.ui_manager.set_highscores(rows)
        self.ui_manager.switch_scene("highscores")

    def _move_pacman(self, action: Action) -> None:
        """Move Pac-Man one tile when movement is valid."""
        if self.current_level is None:
            return

        move_map = {
            Action.MOVE_UP: (0, -1),
            Action.MOVE_DOWN: (0, 1),
            Action.MOVE_LEFT: (-1, 0),
            Action.MOVE_RIGHT: (1, 0),
        }
        move = move_map.get(action)
        if move is None:
            return

        maze = self.current_level.maze
        pacman = self.current_level.pacman
        next_x = pacman.x + move[0]
        next_y = pacman.y + move[1]

        if not maze.can_move(pacman.x, pacman.y, next_x, next_y):
            return

        pacman.move_to(next_x, next_y)
        pacman.direction = self._action_to_direction(action)
        self.state.set_pacman_position(next_x, next_y)

        for pellet in self.current_level.pellets:
            if pellet.is_eaten:
                continue
            if pellet.position != pacman.position:
                continue

            pellet.eat()
            if pellet.is_super:
                self.state.add_score(
                    int(self.config.get("points_per_super_pacgum", 50))
                )
                self._enable_super_mode()
            else:
                self.state.add_score(
                    int(self.config.get("points_per_pacgum", 10))
                )
            break

        self.state.set_pellet_positions(
            [
                pellet.position
                for pellet in self.current_level.pellets
                if not pellet.is_eaten and not pellet.is_super
            ]
        )
        self.state.set_super_pellet_positions(
            [
                pellet.position
                for pellet in self.current_level.pellets
                if not pellet.is_eaten and pellet.is_super
            ]
        )
        self.state.update_pellets(
            len(self.current_level.pellets)
            - (
                len(self.state.pellet_positions)
                + len(self.state.super_pellet_positions)
            ),
            len(self.current_level.pellets),
        )

        if self.state.pellet_positions or self.state.super_pellet_positions:
            return

        if self.level_manager.has_more_levels():
            self.current_level = self.level_manager.advance_level()
            return

        self._show_end_scene("VICTORY")

    @staticmethod
    def _action_to_direction(action: Action) -> Direction:
        """Convert movement actions to directional enum values."""
        if action == Action.MOVE_UP:
            return Direction.UP
        if action == Action.MOVE_DOWN:
            return Direction.DOWN
        if action == Action.MOVE_LEFT:
            return Direction.LEFT
        if action == Action.MOVE_RIGHT:
            return Direction.RIGHT
        return Direction.NONE

    def _enable_super_mode(self) -> None:
        """Enable edible mode on all active ghosts."""
        if self.current_level is None:
            return
        duration = float(self.config.get("super_pacgum_duration", 10))
        for ghost in self.current_level.ghosts:
            if ghost.is_respawning:
                continue
            ghost.become_edible(duration)
        self.state.set_ghost_edible_states(
            [
                ghost.is_edible
                for ghost in self.current_level.ghosts
                if not ghost.is_respawning
            ]
        )
        self.state.set_super_mode_time_remaining(duration)

    def _show_end_scene(self, title: str) -> None:
        """Switch to game over/victory scene without crashing loop."""
        self.state.is_paused = True
        scene = self.ui_manager.scenes.get("game_over")
        if scene is not None:
            set_title = getattr(scene, "set_title", None)
            if callable(set_title):
                set_title(title)
        self.ui_manager.switch_scene("game_over")

    def run(self) -> None:
        """Open the main menu and run the loop."""
        logger.info("Starting game")
        if self.ui_manager.renderer.is_headless():
            logger.warning(
                "No graphics backend available: "
                "exiting immediately in headless mode"
            )
            return

        self.ui_manager.switch_scene("menu")
        self.loop.running = True
        self.loop.run()

    def finish_game(self, player_name: Optional[str] = None) -> None:
        """Persist the current score."""
        if player_name is None:
            player_name = "PLAYER"
        self.highscore_manager.add_score(player_name, self.state.score)
