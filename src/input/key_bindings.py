"""Keyboard bindings for the game."""

from __future__ import annotations

from enum import Enum


class Action(Enum):
    """High-level user actions."""

    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    PAUSE = 4
    SELECT = 5
    BACK = 6
    CHEAT = 7


KEY_MAP = {
    65362: Action.MOVE_UP,
    65364: Action.MOVE_DOWN,
    65361: Action.MOVE_LEFT,
    65363: Action.MOVE_RIGHT,
    ord("w"): Action.MOVE_UP,
    ord("a"): Action.MOVE_LEFT,
    ord("s"): Action.MOVE_DOWN,
    ord("d"): Action.MOVE_RIGHT,
    ord("p"): Action.PAUSE,
    ord(" "): Action.SELECT,
    ord("\r"): Action.SELECT,
    65307: Action.BACK,
    ord("c"): Action.CHEAT,
}
