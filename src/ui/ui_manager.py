"""UI scene manager."""

from __future__ import annotations

from typing import Dict

from src.ui.renderer import Renderer
from src.ui.scenes.game_scene import GameScene
from src.ui.scenes.game_over import GameOverScene
from src.ui.scenes.highscores import HighscoresScene
from src.ui.scenes.instructions import InstructionsScene
from src.ui.scenes.main_menu import MainMenuScene
from src.ui.scenes.pause_menu import PauseMenuScene
from src.ui.scenes.scene import Scene


class UIManager:
    """Hold and switch between active scenes."""

    def __init__(self) -> None:
        self.renderer = Renderer(840, 840)
        self.scenes: Dict[str, Scene] = {
            "menu": MainMenuScene(),
            "game": GameScene(),
            "pause": PauseMenuScene(),
            "highscores": HighscoresScene(),
            "instructions": InstructionsScene(),
            "game_over": GameOverScene(),
        }
        self.current_scene_name = "menu"
        self.current_scene = self.scenes[self.current_scene_name]
        self.current_scene.on_enter()

    def switch_scene(self, scene_name: str) -> None:
        """Switch to another registered scene."""
        if scene_name not in self.scenes:
            return
        self.current_scene.on_exit()
        self.current_scene_name = scene_name
        self.current_scene = self.scenes[scene_name]
        self.current_scene.on_enter()

    def update(self, delta_time: float) -> None:
        """Update active scene."""
        self.current_scene.update(delta_time)

    def render(self) -> None:
        """Render active scene."""
        if self.current_scene_name in ("pause", "game_over"):
            self.scenes["game"].render(self.renderer)
        self.current_scene.render(self.renderer)
        self.renderer.present()

    def handle_input(self, key: int) -> None:
        """Forward input to the active scene."""
        self.current_scene.handle_input(key)

    def set_highscores(self, rows: list[str]) -> None:
        """Inject preformatted highscore rows into highscores scene."""
        scene = self.scenes.get("highscores")
        if scene is None:
            return
        set_rows = getattr(scene, "set_rows", None)
        if callable(set_rows):
            set_rows(rows)
