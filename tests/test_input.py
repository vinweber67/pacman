"""Tests for input handling."""

from types import SimpleNamespace

import pytest

from src.input import input_handler as input_handler_module
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


class FakeEventQueue:
    """Simple fake pygame event queue."""

    def __init__(self) -> None:
        self._events: list[SimpleNamespace] = []

    def set_events(self, events: list[SimpleNamespace]) -> None:
        """Replace queued events."""
        self._events = list(events)

    def get(self) -> list[SimpleNamespace]:
        """Return queued events once."""
        events = list(self._events)
        self._events.clear()
        return events


class FakePressedState:
    """Sparse key state container compatible with pygame indexing."""

    def __init__(self, pressed_keys: set[int]) -> None:
        self.pressed_keys = pressed_keys

    def __getitem__(self, key_code: int) -> int:
        return int(key_code in self.pressed_keys)


class FakeKeyState:
    """Simple fake pygame key state service."""

    def __init__(self) -> None:
        self.pressed_keys: set[int] = set()

    def set_pressed(self, *pressed_keys: int) -> None:
        """Set currently held keys."""
        self.pressed_keys = set(pressed_keys)

    def get_pressed(self) -> FakePressedState:
        """Return the current pressed state."""
        return FakePressedState(self.pressed_keys)


class FakePygame:
    """Minimal pygame double for input polling tests."""

    KEYDOWN = 1
    QUIT = 2
    K_UP = 273
    K_DOWN = 274
    K_LEFT = 276
    K_RIGHT = 275
    K_w = ord("w")
    K_a = ord("a")
    K_s = ord("s")
    K_d = ord("d")
    K_ESCAPE = 27
    K_RETURN = 13
    K_SPACE = 32

    def __init__(self) -> None:
        self.event = FakeEventQueue()
        self.key = FakeKeyState()


class TestHeldMovement:
    """Held-key movement tests."""

    @pytest.fixture(autouse=True)
    def reset_input_handler_state(self) -> None:
        """Reset shared handler state before each test."""
        InputHandler._held_direction_key = None
        InputHandler._next_repeat_at = 0.0
        InputHandler._pygame = None

    def test_poll_events_repeats_held_direction(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Held movement keys should emit repeated direction events."""
        fake_pygame = FakePygame()
        fake_pygame.key.set_pressed(fake_pygame.K_RIGHT)
        fake_pygame.event.set_events(
            [SimpleNamespace(type=fake_pygame.KEYDOWN, key=fake_pygame.K_RIGHT)]
        )

        monotonic_values = iter([1.0, 1.05, 1.19, 1.30])
        monkeypatch.setattr(InputHandler, "_get_pygame", staticmethod(lambda: fake_pygame))
        monkeypatch.setattr(input_handler_module.time, "monotonic", lambda: next(monotonic_values))

        assert InputHandler.poll_events() == [65363]
        assert InputHandler.poll_events() == []
        assert InputHandler.poll_events() == [65363]
        assert InputHandler.poll_events() == [65363]

    def test_poll_events_stops_when_direction_released(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Releasing a movement key should stop synthetic repeats."""
        fake_pygame = FakePygame()
        fake_pygame.key.set_pressed(fake_pygame.K_LEFT)
        fake_pygame.event.set_events(
            [SimpleNamespace(type=fake_pygame.KEYDOWN, key=fake_pygame.K_LEFT)]
        )

        monotonic_values = iter([2.0, 2.25])
        monkeypatch.setattr(InputHandler, "_get_pygame", staticmethod(lambda: fake_pygame))
        monkeypatch.setattr(input_handler_module.time, "monotonic", lambda: next(monotonic_values))

        assert InputHandler.poll_events() == [65361]

        fake_pygame.key.set_pressed()
        assert InputHandler.poll_events() == []
