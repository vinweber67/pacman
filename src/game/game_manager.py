"""Game manager integration layer."""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.cheat.cheat_mode import CheatMode
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
            self.ui_manager.switch_scene("menu")
            self.loop.stop()
            return
        self.current_level = self.level_manager.load_level(
            self.state.current_level,
        )

    def update(self, delta_time: float) -> None:
        """Update the active scene."""
        self.ui_manager.update(delta_time)

    def render(self) -> None:
        """Render the active scene."""
        self.ui_manager.render()

    def handle_input(self, key: int) -> None:
        """Handle raw input events."""
        if key in (65307, ord("q")):
            self.ui_manager.switch_scene("menu")
            self.loop.stop()
            return

        if key == ord("c"):
            CheatMode.skip_level(self.state)
            if self.level_manager.has_more_levels():
                self.current_level = self.level_manager.advance_level()
            else:
                self.state.is_victory = True
                self.loop.stop()
            return

        self.ui_manager.handle_input(key)

    def run(self) -> None:
        """Start a new game and run the loop."""
        logger.info("Starting game")
        if self.ui_manager.renderer.mlx is None:
            logger.warning(
                "No graphics backend available: "
                "exiting immediately in headless mode"
            )
            return

        self.start_game()
        self.loop.run()

    def finish_game(self, player_name: Optional[str] = None) -> None:
        """Persist the current score."""
        if player_name is None:
            player_name = "PLAYER"
        self.highscore_manager.add_score(player_name, self.state.score)
