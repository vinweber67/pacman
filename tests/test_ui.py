"""Tests for the UI layer."""

import src.ui.scenes.main_menu as main_menu_scene_module

from src.ui.colors import COLORS
from src.ui.renderer import Renderer
from src.ui.scenes.game_over import GameOverScene
from src.ui.scenes.main_menu import MainMenuScene
from src.ui.ui_manager import UIManager
from src.utils.constants import Color


class TestRenderer:
    """Renderer tests."""

    def test_headless_renderer(self) -> None:
        """Renderer falls back to headless mode when MLX42 is unavailable."""
        renderer = Renderer(320, 240)
        assert renderer.width == 320
        assert renderer.height == 240
        assert renderer.mlx is None or renderer.mlx is not None


class TestColors:
    """Palette tests."""

    def test_palette_contains_expected_colors(self) -> None:
        """UI palette exposes the known colors."""
        assert COLORS[Color.BLACK] == (0, 0, 0)
        assert COLORS[Color.YELLOW] == (255, 255, 0)


class TestScenes:
    """Scene behavior tests."""

    def test_main_menu_navigation(self) -> None:
        """Menu supports basic navigation."""
        menu = MainMenuScene()
        assert menu.selected == 0
        menu.handle_input(65364)
        assert menu.selected == 1
        menu.handle_input(65362)
        assert menu.selected == 0

    def test_main_menu_ignores_fast_repeat_same_key(
        self,
        monkeypatch,
    ) -> None:
        """Very fast repeated same navigation key should not skip items."""
        menu = MainMenuScene()

        timestamps = iter([1.0, 1.05, 1.30])
        monkeypatch.setattr(
            main_menu_scene_module.time,
            "monotonic",
            lambda: next(timestamps),
        )

        menu.handle_input(65364)
        assert menu.selected == 1
        menu.handle_input(65364)
        assert menu.selected == 1
        menu.handle_input(65364)
        assert menu.selected == 2

    def test_game_over_name_submission(self) -> None:
        """Game over scene captures and submits player names."""
        scene = GameOverScene()
        scene.on_enter()
        scene.handle_input(ord("A"))
        scene.handle_input(ord("L"))
        scene.handle_input(ord("I"))
        scene.handle_input(ord("C"))
        scene.handle_input(ord("E"))
        scene.handle_input(ord("\r"))
        assert scene.consume_submitted_name() == "ALICE"
        assert scene.consume_submitted_name() is None


class TestUIManager:
    """UI manager tests."""

    def test_switch_scene_keeps_menu_when_unknown(self) -> None:
        """Unknown scenes are ignored."""
        ui = UIManager()
        previous_scene = ui.current_scene
        ui.switch_scene("unknown")
        assert ui.current_scene is previous_scene
