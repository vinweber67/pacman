"""Tests for input handling."""

from src.input.input_handler import InputHandler
from src.input.key_bindings import Action


class TestKeyBindings:
    """Key mapping tests."""

    def test_arrow_keys(self) -> None:
        """Arrow keys map to the expected actions."""
        assert InputHandler.key_to_action(65362) == Action.MOVE_UP
        assert InputHandler.key_to_action(65364) == Action.MOVE_DOWN
        assert InputHandler.key_to_action(65361) == Action.MOVE_LEFT
        assert InputHandler.key_to_action(65363) == Action.MOVE_RIGHT

    def test_wasd_keys(self) -> None:
        """WASD keys map to movement actions."""
        assert InputHandler.key_to_action(ord("w")) == Action.MOVE_UP
        assert InputHandler.key_to_action(ord("a")) == Action.MOVE_LEFT
        assert InputHandler.key_to_action(ord("s")) == Action.MOVE_DOWN
        assert InputHandler.key_to_action(ord("d")) == Action.MOVE_RIGHT

    def test_special_keys(self) -> None:
        """Special keys map to menu or cheat actions."""
        assert InputHandler.key_to_action(ord("p")) == Action.PAUSE
        assert InputHandler.key_to_action(ord(" ")) == Action.SELECT
        assert InputHandler.key_to_action(65307) == Action.BACK
        assert InputHandler.key_to_action(ord("c")) == Action.CHEAT

    def test_unknown_key(self) -> None:
        """Unknown keys return None."""
        assert InputHandler.key_to_action(99999) is None
