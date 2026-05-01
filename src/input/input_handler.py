"""Input handling helpers."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Optional

from src.input.key_bindings import Action, KEY_MAP


class InputHandler:
    """Convert raw keys to game actions."""

    _pygame: Optional[Any] = None

    @staticmethod
    def _get_pygame() -> Optional[Any]:
        """Lazy-load pygame module if available."""
        if InputHandler._pygame is not None:
            return InputHandler._pygame
        try:
            InputHandler._pygame = import_module("pygame")
        except Exception:
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
    def poll_events() -> list[int]:
        """Return the list of key events.

        Reads KEYDOWN events from pygame when available.
        """
        pygame = InputHandler._get_pygame()
        if pygame is None:
            return []

        events: list[int] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append(65307)
            elif event.type == pygame.KEYDOWN:
                events.append(InputHandler._normalize_pygame_key(event.key))
        return events

    @staticmethod
    def key_to_action(key: int) -> Optional[Action]:
        """Map a raw key code to an action."""
        return KEY_MAP.get(key)
