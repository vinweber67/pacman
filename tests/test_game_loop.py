"""Tests for game loop and level progression."""

from src.game.game_loop import GameLoop
from src.game.game_manager import GameManager
from src.game.game_state import GameState
from src.game.level_manager import LevelManager


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
        manager.state.score = 123
        manager.finish_game("ALICE")
        assert any(
            entry.name == "ALICE" and entry.score == 123
            for entry in manager.highscore_manager.scores
        )
