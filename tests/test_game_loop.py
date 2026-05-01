"""Tests for game loop and level progression."""

from pathlib import Path

import pytest

from src.entities.ai.ghost_behavior import GhostAI
from src.entities.ghost import Ghost
from src.entities.pacman import Pacman
from src.entities.pellet import Pellet
from src.game.game_loop import GameLoop
from src.game.game_manager import GameManager
from src.game.game_state import GameState
from src.game.level_manager import LevelManager
from src.input.key_bindings import Action
from src.maze.maze import Maze
from src.maze.maze_generator import MazeGenerator


CONFIG = {
    "highscore_filename": ".data/highscores.json",
    "levels": [
        {"width": 7, "height": 7, "seed": 42, "max_time": 12},
        {"width": 9, "height": 9, "seed": 7, "max_time": 15},
    ],
    "pacgum_count": 5,
}

MINIMAL_CONFIG = {
    "levels": [
        {"width": 7, "height": 7, "seed": 42, "max_time": 5},
    ],
}


class TestLevelManager:
    """Level manager tests."""

    def test_load_first_level(self) -> None:
        """The first level loads resources and updates state."""
        state = GameState()
        state.reset()
        manager = LevelManager(CONFIG)
        level = manager.load_level(1)
        assert level.maze.width == 7
        assert state.current_level == 1
        assert state.level_time_remaining == 12
        assert len(level.pellets) == 5

    def test_advance_level(self) -> None:
        """Advancing loads the next level."""
        state = GameState()
        state.reset()
        manager = LevelManager(CONFIG)
        manager.load_level(1)
        next_level = manager.advance_level()
        assert state.current_level == 2
        assert next_level.maze.width == 9

    def test_level_one_fixed_seed_and_following_levels_random(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Level 1 keeps configured seed, level 2+ resolves random seed."""
        generated_seeds: list[int] = []

        def fake_generate(width: int, height: int, seed: int) -> Maze:
            generated_seeds.append(seed)
            return Maze(width, height)

        monkeypatch.setattr(
            MazeGenerator,
            "generate",
            staticmethod(fake_generate),
        )
        monkeypatch.setattr(
            LevelManager,
            "_create_random_seed",
            staticmethod(lambda: 1337),
        )

        state = GameState()
        state.reset()
        manager = LevelManager(CONFIG)
        manager.load_level(1)
        manager.advance_level()

        assert generated_seeds == [42, 1337]

    def test_load_level_with_minimal_config_defaults(self) -> None:
        """Minimal config should still load a playable level."""
        state = GameState()
        state.reset()
        manager = LevelManager(MINIMAL_CONFIG)
        level = manager.load_level(1)

        assert level.maze.width == 7
        assert state.lives == 3
        assert len(level.pellets) == 42

    def test_load_level_with_very_few_pellets(self) -> None:
        """Levels with very few pellets should still be playable."""
        state = GameState()
        state.reset()
        manager = LevelManager({**CONFIG, "pacgum_count": 1})
        level = manager.load_level(1)

        assert len(level.pellets) == 1


class TestGameLoop:
    """Game loop tests."""

    def test_step_updates_and_renders(self) -> None:
        """A step updates the manager and decreases time."""
        manager = GameManager(CONFIG)
        manager.start_game()
        loop = GameLoop(manager)
        loop.step(1.0, keys=[])
        assert GameState().level_time_remaining == 11

    def test_step_paused_only_renders(self) -> None:
        """Paused state keeps the game from updating time."""
        manager = GameManager(CONFIG)
        manager.start_game()
        state = GameState()
        state.pause()
        loop = GameLoop(manager)
        previous_time = state.level_time_remaining
        loop.step(1.0, keys=[])
        assert state.level_time_remaining == previous_time

    def test_step_no_time_limit_keeps_timer(self) -> None:
        """No-time-limit cheat prevents timer decrease."""
        manager = GameManager(CONFIG)
        manager.start_game()
        state = GameState()
        state.no_time_limit = True
        loop = GameLoop(manager)
        previous_time = state.level_time_remaining
        loop.step(1.0, keys=[])
        assert state.level_time_remaining == previous_time

    def test_timeout_consumes_life(self) -> None:
        """Timeout triggers the manager callback."""
        manager = GameManager(CONFIG)
        manager.start_game()
        state = GameState()
        state.level_time_remaining = 1
        loop = GameLoop(manager)
        loop.step(1.0, keys=[])
        assert state.lives == 2

    def test_short_timer_restarts_same_level(self) -> None:
        """A very short timer should restart the current level after timeout."""
        short_timer_config = {
            **CONFIG,
            "levels": [
                {"width": 7, "height": 7, "seed": 42, "max_time": 1},
            ],
        }
        manager = GameManager(short_timer_config)
        manager.start_game()
        state = GameState()
        loop = GameLoop(manager)

        loop.step(1.0, keys=[])

        assert state.current_level == 1
        assert state.level_time_remaining == 1


class TestGameManagerIntegration:
    """Game manager integration tests."""

    def test_menu_navigation_with_arrow_keys(self) -> None:
        """Arrow keys navigate menu when gameplay has not started."""
        manager = GameManager(CONFIG)
        menu = manager.ui_manager.current_scene
        assert getattr(menu, "selected", None) == 0
        manager.handle_input(65364)
        assert getattr(menu, "selected", None) == 1

    def test_start_game_switches_scene(self) -> None:
        """Starting a run activates gameplay scene."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.ui_manager.current_scene_name == "game"
        assert manager.loop.running is True

    def test_main_menu_start_victory_highscore_menu_cycle(
        self,
        tmp_path: Path,
    ) -> None:
        """A full menu -> start -> victory -> highscores -> menu flow works."""
        config = {
            **CONFIG,
            "highscore_filename": str(tmp_path / "cycle-highscores.json"),
            "levels": [
                {"width": 7, "height": 7, "seed": 42, "max_time": 12},
            ],
            "pacgum_count": 1,
        }
        manager = GameManager(config)

        assert manager.ui_manager.current_scene_name == "menu"
        manager.handle_input(ord("\r"))
        assert manager.ui_manager.current_scene_name == "game"
        assert manager.current_level is not None

        level = manager.current_level
        pacman = level.pacman
        target = level.maze.get_neighbors(pacman.x, pacman.y)[0]
        level.pellets = [Pellet(target[0], target[1])]
        if target[0] > pacman.x:
            action = Action.MOVE_RIGHT
        elif target[0] < pacman.x:
            action = Action.MOVE_LEFT
        elif target[1] > pacman.y:
            action = Action.MOVE_DOWN
        else:
            action = Action.MOVE_UP

        manager._move_pacman(action)
        assert manager.ui_manager.current_scene_name == "game_over"

        for key in [ord("E"), ord("V"), ord("E"), ord("\r")]:
            manager.handle_input(key)

        assert manager.ui_manager.current_scene_name == "menu"

        manager.handle_input(65364)
        manager.handle_input(ord("\r"))
        assert manager.ui_manager.current_scene_name == "highscores"

        manager.handle_input(65307)
        assert manager.ui_manager.current_scene_name == "menu"

    def test_cheat_skip_advances_level(self) -> None:
        """The cheat key advances to the next level."""
        manager = GameManager(CONFIG)
        manager.start_game()
        manager.handle_input(ord("c"))
        assert GameState().current_level == 2

    def test_quit_key_stops_loop(self) -> None:
        """Pressing q cleanly stops the loop."""
        manager = GameManager(CONFIG)
        manager.start_game()
        manager.handle_input(ord("q"))
        assert manager.loop.running is False

    def test_finish_game_saves_score(self) -> None:
        """Finishing a game writes a score entry."""
        manager = GameManager(CONFIG)
        manager.start_game()
        manager.state.score = 999999
        manager.finish_game("ALICE")
        assert any(
            entry.name == "ALICE" and entry.score == 999999
            for entry in manager.highscore_manager.scores
        )

    def test_game_over_name_entry_saves_and_returns_menu(
        self,
        tmp_path: Path,
    ) -> None:
        """Submitting name on end scene saves score and returns to menu."""
        config = {
            **CONFIG,
            "highscore_filename": str(tmp_path / "highscores.json"),
        }
        manager = GameManager(config)
        manager.start_game()
        manager.state.score = 456
        manager._show_end_scene("GAME OVER")

        for key in [ord("B"), ord("O"), ord("B"), ord("\r")]:
            manager.handle_input(key)

        assert manager.ui_manager.current_scene_name == "menu"
        assert any(
            entry.name == "BOB" and entry.score == 456
            for entry in manager.highscore_manager.scores
        )

    def test_super_pellet_makes_ghosts_edible(self) -> None:
        """Eating a super pellet increases score and enables edible mode."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        level = manager.current_level
        pacman = level.pacman
        neighbors = level.maze.get_neighbors(pacman.x, pacman.y)
        assert neighbors
        target = neighbors[0]

        level.pellets = [
            Pellet(target[0], target[1], is_super=True),
            Pellet(pacman.x, pacman.y + 2),
        ]
        previous_score = manager.state.score
        if target[0] > pacman.x:
            action = Action.MOVE_RIGHT
        elif target[0] < pacman.x:
            action = Action.MOVE_LEFT
        elif target[1] > pacman.y:
            action = Action.MOVE_DOWN
        else:
            action = Action.MOVE_UP
        manager._move_pacman(action)

        assert manager.state.score == (
            previous_score + 50
        )
        assert all(ghost.is_edible for ghost in level.ghosts)
        assert all(manager.state.ghost_edible_states)
        assert manager.state.super_mode_time_remaining > 0.0

    def test_show_all_paths_toggle_populates_overlay(self) -> None:
        """Path overlay cheat should populate ghost path visualization data."""
        manager = GameManager(CONFIG)
        manager.start_game()

        manager.handle_input(ord("v"))
        manager.update(0.01)

        assert manager.state.show_all_paths is True
        assert manager.state.ghost_path_overlays
        assert all(len(path) >= 2 for path in manager.state.ghost_path_overlays)

    def test_cheat_overlay_toggle_via_input(self) -> None:
        """Cheat overlay can be hidden and shown again from gameplay input."""
        manager = GameManager(CONFIG)
        manager.start_game()

        assert manager.state.cheat_overlay_visible is True
        manager.handle_input(ord("h"))
        assert manager.state.cheat_overlay_visible is False
        manager.handle_input(ord("h"))
        assert manager.state.cheat_overlay_visible is True

    def test_super_mode_timer_counts_down(self) -> None:
        """Super mode timer should decrease as gameplay updates."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        level = manager.current_level
        for ghost in level.ghosts:
            ghost.become_edible(1.5)
        manager.state.set_super_mode_time_remaining(1.5)

        manager.update(0.5)
        assert 0.9 <= manager.state.super_mode_time_remaining <= 1.1

    def test_pacman_ghost_super_pellet_same_tile_edge_case(self) -> None:
        """A super pellet on the ghost tile should make the ghost edible first."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        level = manager.current_level
        pacman = level.pacman
        target = level.maze.get_neighbors(pacman.x, pacman.y)[0]
        ghost = level.ghosts[0]
        ghost.move_to(target[0], target[1])
        level.pellets = [Pellet(target[0], target[1], is_super=True), Pellet(1, 1)]

        previous_score = manager.state.score
        if target[0] > pacman.x:
            action = Action.MOVE_RIGHT
        elif target[0] < pacman.x:
            action = Action.MOVE_LEFT
        elif target[1] > pacman.y:
            action = Action.MOVE_DOWN
        else:
            action = Action.MOVE_UP

        manager._move_pacman(action)
        manager._check_ghost_collisions()

        assert manager.state.score == previous_score + 250
        assert ghost.is_respawning is True
        assert manager.state.ghost_respawn_positions == [(ghost.spawn_x, ghost.spawn_y)]

    def test_multiple_nearby_super_pellets_refresh_super_mode(self) -> None:
        """Eating nearby super pellets should refresh the edible timer."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        level = manager.current_level
        pacman = level.pacman
        neighbors = level.maze.get_neighbors(pacman.x, pacman.y)
        first_target = neighbors[0]
        second_target = level.maze.get_neighbors(first_target[0], first_target[1])[0]
        if second_target == pacman.position:
            second_target = level.maze.get_neighbors(first_target[0], first_target[1])[1]

        level.pellets = [
            Pellet(first_target[0], first_target[1], is_super=True),
            Pellet(second_target[0], second_target[1], is_super=True),
            Pellet(1, 1),
        ]

        def action_to(target_x: int, target_y: int) -> Action:
            if target_x > pacman.x:
                return Action.MOVE_RIGHT
            if target_x < pacman.x:
                return Action.MOVE_LEFT
            if target_y > pacman.y:
                return Action.MOVE_DOWN
            return Action.MOVE_UP

        manager._move_pacman(action_to(first_target[0], first_target[1]))
        first_timer = manager.state.super_mode_time_remaining
        manager.update(0.5)
        pacman = level.pacman
        manager._move_pacman(action_to(second_target[0], second_target[1]))

        assert manager.state.super_mode_time_remaining >= first_timer - 0.1

    def test_edible_ghost_collision_respawns(self) -> None:
        """Colliding with edible ghost awards score and triggers respawn."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        level = manager.current_level
        ghost = level.ghosts[0]
        ghost.move_to(level.pacman.x, level.pacman.y)
        ghost.become_edible(2.0)

        previous_score = manager.state.score
        manager._check_ghost_collisions()

        assert manager.state.score == (
            previous_score + 200
        )
        assert ghost.is_respawning is True

    def test_non_edible_ghost_collision_costs_life(self) -> None:
        """Colliding with a normal ghost should consume one life."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        level = manager.current_level
        ghost = level.ghosts[0]
        ghost.move_to(level.pacman.x, level.pacman.y)

        previous_lives = manager.state.lives
        manager._check_ghost_collisions()
        assert manager.state.lives == previous_lives - 1
        center = level.maze.get_center()
        assert manager.state.pacman_position == center

    def test_ghosts_move_autonomously_in_corridors(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Ghosts should move automatically and only through valid links."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        level = manager.current_level
        initial_positions = [ghost.position for ghost in level.ghosts]

        def deterministic_move(
            ghost: Ghost,
            pacman: Pacman,
            maze: Maze,
        ) -> tuple[int, int] | None:
            del pacman
            neighbors = maze.get_neighbors(ghost.x, ghost.y)
            return neighbors[0] if neighbors else None

        monkeypatch.setattr(
            GhostAI,
            "calculate_next_move",
            staticmethod(deterministic_move),
        )

        manager.update(0.2)
        moved_positions = [ghost.position for ghost in level.ghosts]

        assert any(
            before != after
            for before, after in zip(initial_positions, moved_positions)
        )
        for before, after in zip(initial_positions, moved_positions):
            if before == after:
                continue
            assert level.maze.can_move(before[0], before[1], after[0], after[1])

    def test_respawning_ghost_skips_moves_others_continue(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A respawning ghost stays hidden while others keep moving."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        level = manager.current_level
        ghost_to_respawn = level.ghosts[0]
        other_ghost = level.ghosts[1]
        other_start = other_ghost.position

        ghost_to_respawn.move_to(level.pacman.x, level.pacman.y)
        ghost_to_respawn.become_edible(2.0)
        manager._check_ghost_collisions()

        assert ghost_to_respawn.is_respawning is True

        def deterministic_move(
            ghost: Ghost,
            pacman: Pacman,
            maze: Maze,
        ) -> tuple[int, int] | None:
            del pacman
            if ghost.is_respawning:
                return None
            neighbors = maze.get_neighbors(ghost.x, ghost.y)
            return neighbors[0] if neighbors else None

        monkeypatch.setattr(
            GhostAI,
            "calculate_next_move",
            staticmethod(deterministic_move),
        )

        manager.update(0.2)

        assert ghost_to_respawn.position == (-1, -1)
        assert manager.state.ghost_respawn_positions == [
            (ghost_to_respawn.spawn_x, ghost_to_respawn.spawn_y)
        ]
        assert other_ghost.position != other_start

    def test_ghost_in_corner_when_pacman_arrives(self) -> None:
        """Colliding with a ghost still works when the ghost sits on a corner."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        level = manager.current_level
        ghost = level.ghosts[0]
        ghost.move_to(1, 1)
        level.pacman.move_to(1, 2)
        manager.state.set_pacman_position(1, 2)

        manager._move_pacman(Action.MOVE_UP)
        manager._check_ghost_collisions()

        assert manager.state.lives == 2
        assert manager.state.pacman_position == level.maze.get_center()

    def test_last_life_collision_shows_game_over(self) -> None:
        """Collision on last life opens the game over scene."""
        manager = GameManager(CONFIG)
        manager.start_game()
        assert manager.current_level is not None

        manager.state.lives = 1
        level = manager.current_level
        ghost = level.ghosts[0]
        ghost.move_to(level.pacman.x, level.pacman.y)

        manager._check_ghost_collisions()
        assert manager.state.is_game_over is True
        assert manager.ui_manager.current_scene_name == "game_over"
