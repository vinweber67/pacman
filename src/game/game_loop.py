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

        keys = keys or InputHandler.poll_events()
        for key in keys:
            self.game_manager.handle_input(key)

        if self.state.is_paused:
            self.game_manager.render()
            return

        if not self.state.no_time_limit:
            self._elapsed_time += delta_time
            if self._elapsed_time >= 1.0:
                elapsed_seconds = int(self._elapsed_time)
                self._elapsed_time -= elapsed_seconds
                self.state.level_time_remaining = max(
                    0,
                    self.state.level_time_remaining - elapsed_seconds,
                )

        self.game_manager.update(delta_time)
        self.game_manager.render()

        if self.state.level_time_remaining == 0:
            self.game_manager.on_level_timeout()

    def run(self, max_frames: Optional[int] = None) -> None:
        """Run until stopped or the optional frame budget is reached."""
        frame_count = 0
        previous_time = time.perf_counter()
        while self.running:
            frame_start = time.perf_counter()
            delta_time = max(0.0, frame_start - previous_time)
            previous_time = frame_start

            # Clamp unusually large frame gaps so temporary stalls do not
            # produce visibly abrupt simulation jumps.
            self.step(min(delta_time, FRAME_TIME * 4.0))
            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                break

            frame_elapsed = time.perf_counter() - frame_start
            remaining_time = FRAME_TIME - frame_elapsed
            # Sleep for most of the wait, then spin-wait the last millisecond
            # for sub-millisecond precision — eliminates OS sleep overshoot.
            if remaining_time > 0.001:
                time.sleep(remaining_time - 0.001)
            while time.perf_counter() - frame_start < FRAME_TIME:
                time.sleep(0)

    def stop(self) -> None:
        """Stop the game loop."""
        logger.info("Stopping game loop")
        self.running = False
