"""Input handling helpers."""

from __future__ import annotations

from typing import Optional

from src.input.key_bindings import Action, KEY_MAP


class InputHandler:
    """Convert raw keys to game actions."""

    @staticmethod
    def poll_events() -> list[int]:
        """Return the list of key events.

        The real backend is not wired yet, so this remains a placeholder.
        """
        return []

    @staticmethod
    def key_to_action(key: int) -> Optional[Action]:
        """Map a raw key code to an action."""
        return KEY_MAP.get(key)
