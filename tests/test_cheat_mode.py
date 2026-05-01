"""Tests for cheat mode helpers."""

from __future__ import annotations

from src.cheat.cheat_mode import CheatMode
from src.game.game_state import GameState


def test_toggle_invincibility() -> None:
    """Invincibility toggles on and off."""
    state = GameState()
    state.reset()

    assert state.is_invincible is False
    CheatMode.toggle_invincibility(state)
    assert state.is_invincible is True
    CheatMode.toggle_invincibility(state)
    assert state.is_invincible is False


def test_freeze_ghosts_toggle() -> None:
    """Ghost freeze toggles on and off."""
    state = GameState()
    state.reset()

    assert state.are_ghosts_frozen is False
    CheatMode.freeze_ghosts(state)
    assert state.are_ghosts_frozen is True
    CheatMode.freeze_ghosts(state)
    assert state.are_ghosts_frozen is False


def test_add_lives() -> None:
    """Adding lives increases life count only for positive values."""
    state = GameState()
    state.reset()

    CheatMode.add_lives(state, 2)
    assert state.lives == 5

    CheatMode.add_lives(state, -3)
    assert state.lives == 5


def test_increase_speed() -> None:
    """Speed multiplier increases only for valid factors."""
    state = GameState()
    state.reset()

    CheatMode.increase_speed(state, 2.0)
    assert state.player_speed_multiplier == 2.0

    CheatMode.increase_speed(state, 0.0)
    assert state.player_speed_multiplier == 2.0


def test_skip_level() -> None:
    """Skip level increments current level."""
    state = GameState()
    state.reset()

    assert state.current_level == 1
    CheatMode.skip_level(state)
    assert state.current_level == 2
