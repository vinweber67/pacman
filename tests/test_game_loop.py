"""Tests for game loop and level progression."""

import pytest

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

    def test_timeout_consumes_life(self) -> None:
        """Timeout triggers the manager callback."""
        manager = GameManager(CONFIG)
        manager.start_game()
        state = GameState()
        state.level_time_remaining = 1
        loop = GameLoop(manager)
        loop.step(1.0, keys=[])
        assert state.lives == 2


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

    def test_game_over_name_entry_saves_and_returns_menu(self) -> None:
        """Submitting name on end scene saves score and returns to menu."""
        manager = GameManager(CONFIG)
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
        assert manager.state.super_mode_time_remaining > 0.0

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
