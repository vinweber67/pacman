"""Main game loop implementation."""

from __future__ import annotations

import time
from typing import Optional, Protocol

from src.game.game_state import GameState
from src.input.input_handler import InputHandler
from src.utils.constants import FRAME_TIME
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GameLoopManager(Protocol):
    """Protocol required by the loop."""

    def handle_input(self, key: int) -> None:
        """Handle raw input."""

    def update(self, delta_time: float) -> None:
        """Update the current scene."""

    def render(self) -> None:
        """Render the current scene."""

    def on_level_timeout(self) -> None:
        """Handle a level timeout."""


class GameLoop:
    """Run the main update/render loop."""

    def __init__(self, game_manager: GameLoopManager) -> None:
        self.game_manager = game_manager
        self.state = GameState()
        self.running = False
        self._elapsed_time = 0.0

    def step(
        self,
        delta_time: float,
        keys: Optional[list[int]] = None,
    ) -> None:
        """Advance the simulation by one step."""
        if not self.running:
            self.running = True

        if self.state.is_game_over or self.state.is_victory:
            self.running = False
            return

        keys = keys or InputHandler.poll_events()
        for key in keys:
            self.game_manager.handle_input(key)

        if self.state.is_paused:
            self.game_manager.render()
            return

        self._elapsed_time += delta_time
        self.state.level_time_remaining = max(
            0,
            self.state.level_time_remaining - int(delta_time),
        )

        self.game_manager.update(delta_time)
        self.game_manager.render()

        if self.state.level_time_remaining == 0:
            self.game_manager.on_level_timeout()

    def run(self, max_frames: Optional[int] = None) -> None:
        """Run until stopped or the optional frame budget is reached."""
        frame_count = 0
        while self.running:
            self.step(FRAME_TIME)
            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                break
            time.sleep(FRAME_TIME)

    def stop(self) -> None:
        """Stop the game loop."""
        logger.info("Stopping game loop")
        self.running = False
