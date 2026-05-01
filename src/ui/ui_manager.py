"""UI scene manager."""

from __future__ import annotations

from typing import Dict

from src.ui.renderer import Renderer
from src.ui.scenes.game_scene import GameScene
from src.ui.scenes.main_menu import MainMenuScene
from src.ui.scenes.scene import Scene


class UIManager:
    """Hold and switch between active scenes."""

    def __init__(self) -> None:
        self.renderer = Renderer(840, 840)
        self.scenes: Dict[str, Scene] = {
            "menu": MainMenuScene(),
            "game": GameScene(),
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
        self.current_scene.render(self.renderer)
        self.renderer.present()

    def handle_input(self, key: int) -> None:
        """Forward input to the active scene."""
        self.current_scene.handle_input(key)
