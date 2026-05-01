"""Input handling helpers."""

from __future__ import annotations

from importlib import import_module
import time
from typing import Any, Optional

from src.input.key_bindings import Action, KEY_MAP


class InputHandler:
    """Convert raw keys to game actions."""

    _pygame: Optional[Any] = None
    _held_direction_key: Optional[int] = None
    _next_repeat_at: float = 0.0
    _repeat_delay: float = 0.18
    _repeat_interval: float = 0.1

    _pygame_direction_keys = (
        ("K_UP", 65362),
        ("K_DOWN", 65364),
        ("K_LEFT", 65361),
        ("K_RIGHT", 65363),
        ("K_w", ord("w")),
        ("K_a", ord("a")),
        ("K_s", ord("s")),
        ("K_d", ord("d")),
    )

    @staticmethod
    def _get_pygame() -> Optional[Any]:
        """Lazy-load pygame module if available."""
        if InputHandler._pygame is not None:
            return InputHandler._pygame
        try:
            InputHandler._pygame = import_module("pygame")
        except ImportError:
            InputHandler._pygame = None
        return InputHandler._pygame

    @staticmethod
    def _normalize_pygame_key(key: int) -> int:
        """Map pygame key codes to the project's expected key space."""
        pygame = InputHandler._get_pygame()
        if pygame is None:
            return key

        special_map = {
            pygame.K_UP: 65362,
            pygame.K_DOWN: 65364,
            pygame.K_LEFT: 65361,
            pygame.K_RIGHT: 65363,
            pygame.K_ESCAPE: 65307,
            pygame.K_RETURN: ord("\r"),
            pygame.K_SPACE: ord(" "),
        }
        return special_map.get(key, key)

    @staticmethod
    def _is_direction_action(key: int) -> bool:
        """Return whether a key represents directional movement."""
        action = InputHandler.key_to_action(key)
        return action in {
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        }

    @staticmethod
    def _is_pressed(pressed_state: Any, key_code: int) -> bool:
        """Return whether a pygame key state reports a pressed key."""
        try:
            return bool(pressed_state[key_code])
        except (KeyError, IndexError, TypeError):
            return False

    @staticmethod
    def _get_pressed_direction_keys(pygame: Any) -> list[int]:
        """Return currently pressed movement keys in a stable order."""
        pressed_state = pygame.key.get_pressed()
        pressed_keys: list[int] = []
        for attribute_name, normalized_key in InputHandler._pygame_direction_keys:
            pygame_key = getattr(pygame, attribute_name, None)
            if pygame_key is None:
                continue
            if not InputHandler._is_pressed(pressed_state, pygame_key):
                continue
            if normalized_key not in pressed_keys:
                pressed_keys.append(normalized_key)
        return pressed_keys

    @staticmethod
    def _update_held_direction(
        pressed_direction_keys: list[int],
        current_time: float,
    ) -> None:
        """Synchronize held-direction state with the currently pressed keys."""
        if not pressed_direction_keys:
            InputHandler._held_direction_key = None
            InputHandler._next_repeat_at = 0.0
            return

        if InputHandler._held_direction_key in pressed_direction_keys:
            return

        InputHandler._held_direction_key = pressed_direction_keys[0]
        InputHandler._next_repeat_at = current_time + InputHandler._repeat_delay

    @staticmethod
    def poll_events() -> list[int]:
        """Return the list of key events.

        Reads KEYDOWN events from pygame when available and synthesizes
        repeat events for held movement keys.
        """
        pygame = InputHandler._get_pygame()
        if pygame is None:
            return []

        current_time = time.monotonic()
        events: list[int] = []
        direction_keydown_seen = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append(65307)
            elif event.type == pygame.KEYDOWN:
                normalized_key = InputHandler._normalize_pygame_key(event.key)
                events.append(normalized_key)
                if InputHandler._is_direction_action(normalized_key):
                    InputHandler._held_direction_key = normalized_key
                    InputHandler._next_repeat_at = (
                        current_time + InputHandler._repeat_delay
                    )
                    direction_keydown_seen = True

        pressed_direction_keys = InputHandler._get_pressed_direction_keys(pygame)
        InputHandler._update_held_direction(pressed_direction_keys, current_time)

        if (
            not direction_keydown_seen
            and InputHandler._held_direction_key is not None
            and current_time >= InputHandler._next_repeat_at
        ):
            events.append(InputHandler._held_direction_key)
            InputHandler._next_repeat_at = (
                current_time + InputHandler._repeat_interval
            )
        return events

    @staticmethod
    def key_to_action(key: int) -> Optional[Action]:
        """Map a raw key code to an action."""
        return KEY_MAP.get(key)
