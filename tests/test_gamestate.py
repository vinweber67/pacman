"""Tests for GameState singleton."""

from src.game.game_state import GameState


class TestGameStateSingleton:
    """Test GameState singleton pattern."""

    def test_singleton_instance(self) -> None:
        """Test that GameState is a singleton."""
        state1 = GameState()
        state2 = GameState()
        assert state1 is state2, "GameState should return same instance"

    def test_singleton_persistence(self) -> None:
        """Test that singleton persists across instances."""
        state1 = GameState()
        state1.score = 100
        state2 = GameState()
        assert state2.score == 100, "State should persist"

    def test_singleton_reset(self) -> None:
        """Test that reset clears singleton state."""
        state = GameState()
        state.score = 500
        state.lives = 1
        state.reset()
        assert state.score == 0
        assert state.lives == 3


class TestGameStateScore:
    """Test score management."""

    def test_add_score_positive(self) -> None:
        """Test adding positive points."""
        state = GameState()
        state.score = 0
        state.add_score(10)
        assert state.score == 10

    def test_add_score_multiple(self) -> None:
        """Test adding multiple scores."""
        state = GameState()
        state.score = 0
        state.add_score(10)
        state.add_score(20)
        state.add_score(5)
        assert state.score == 35

    def test_add_score_negative_clamped(self) -> None:
        """Test that negative scores are clamped to 0."""
        state = GameState()
        state.score = 0
        state.add_score(-10)
        assert state.score == 0

    def test_add_score_large_value(self) -> None:
        """Test adding large score."""
        state = GameState()
        state.score = 0
        state.add_score(999999)
        assert state.score == 999999


class TestGameStateLives:
    """Test lives management."""

    def test_lose_life_decreases(self) -> None:
        """Test that losing life decreases count."""
        state = GameState()
        state.lives = 3
        state.lose_life()
        assert state.lives == 2

    def test_lose_life_multiple(self) -> None:
        """Test losing multiple lives."""
        state = GameState()
        state.lives = 3
        state.lose_life()
        state.lose_life()
        assert state.lives == 1

    def test_lose_life_game_over(self) -> None:
        """Test game over when no lives left."""
        state = GameState()
        state.lives = 1
        state.is_game_over = False
        state.lose_life()
        assert state.lives == 0
        assert state.is_game_over is True


class TestGameStateLevel:
    """Test level progression."""

    def test_next_level_increases(self) -> None:
        """Test that next_level increases level."""
        state = GameState()
        state.current_level = 1
        state.next_level()
        assert state.current_level == 2

    def test_next_level_resets_timer(self) -> None:
        """Test that next_level resets timer."""
        state = GameState()
        state.level_time_remaining = 10
        state.next_level()
        assert state.level_time_remaining == 90

    def test_next_level_multiple(self) -> None:
        """Test progressing through multiple levels."""
        state = GameState()
        state.current_level = 1
        for _ in range(3):
            state.next_level()
        assert state.current_level == 4


class TestGameStatePositions:
    """Test position management."""

    def test_set_pacman_position(self) -> None:
        """Test setting Pacman position."""
        state = GameState()
        state.set_pacman_position(5, 10)
        assert state.pacman_position == (5, 10)

    def test_set_ghost_positions(self) -> None:
        """Test setting ghost positions."""
        state = GameState()
        positions = [(0, 0), (1, 1), (2, 2)]
        state.set_ghost_positions(positions)
        assert state.ghost_positions == positions

    def test_set_ghost_edible_states(self) -> None:
        """Test setting ghost edible render flags."""
        state = GameState()
        edible_states = [False, True, False]
        state.set_ghost_edible_states(edible_states)
        assert state.ghost_edible_states == edible_states

    def test_set_ghost_respawn_positions(self) -> None:
        """Test setting ghost respawn render positions."""
        state = GameState()
        respawn_positions = [(1, 1), (5, 5)]
        state.set_ghost_respawn_positions(respawn_positions)
        assert state.ghost_respawn_positions == respawn_positions

    def test_pacman_position_default(self) -> None:
        """Test default Pacman position."""
        state = GameState()
        state.reset()
        assert state.pacman_position == (10, 10)


class TestGameStatePause:
    """Test pause functionality."""

    def test_pause_sets_flag(self) -> None:
        """Test pause sets is_paused flag."""
        state = GameState()
        state.is_paused = False
        state.pause()
        assert state.is_paused is True

    def test_resume_clears_flag(self) -> None:
        """Test resume clears is_paused flag."""
        state = GameState()
        state.is_paused = True
        state.resume()
        assert state.is_paused is False

    def test_toggle_pause_from_playing(self) -> None:
        """Test toggle pause from playing state."""
        state = GameState()
        state.is_paused = False
        state.toggle_pause()
        assert state.is_paused is True

    def test_toggle_pause_from_paused(self) -> None:
        """Test toggle pause from paused state."""
        state = GameState()
        state.is_paused = True
        state.toggle_pause()
        assert state.is_paused is False


class TestGameStatePellets:
    """Test pellet management."""

    def test_update_pellets(self) -> None:
        """Test updating pellet counters."""
        state = GameState()
        state.update_pellets(20, 50)
        assert state.pellets_eaten == 20
        assert state.pellets_total == 50

    def test_update_pellets_zero(self) -> None:
        """Test updating to zero pellets."""
        state = GameState()
        state.update_pellets(0, 0)
        assert state.pellets_eaten == 0
        assert state.pellets_total == 0


class TestGameStateReset:
    """Test reset functionality."""

    def test_reset_all_values(self) -> None:
        """Test reset sets all values to defaults."""
        state = GameState()
        # Modify state
        state.score = 500
        state.lives = 1
        state.current_level = 5
        state.is_paused = True
        state.is_game_over = True
        state.pellets_eaten = 10
        state.pellets_total = 42

        # Reset
        state.reset()

        # Verify defaults
        assert state.score == 0
        assert state.lives == 3
        assert state.current_level == 1
        assert state.level_time_remaining == 90
        assert state.is_paused is False
        assert state.is_game_over is False
        assert state.is_victory is False
        assert state.pellets_eaten == 0
        assert state.pellets_total == 0


class TestGameStateStatus:
    """Test status reporting."""

    def test_get_status_dict(self) -> None:
        """Test get_status returns dictionary."""
        state = GameState()
        status = state.get_status()
        assert isinstance(status, dict)
        assert "score" in status
        assert "lives" in status
        assert "level" in status

    def test_get_status_values(self) -> None:
        """Test get_status returns correct values."""
        state = GameState()
        state.score = 150
        state.lives = 2
        state.current_level = 3
        status = state.get_status()
        assert status["score"] == 150
        assert status["lives"] == 2
        assert status["level"] == 3

    def test_get_status_all_keys(self) -> None:
        """Test get_status includes all keys."""
        state = GameState()
        status = state.get_status()
        required_keys = [
            "score", "lives", "level", "time_remaining",
            "is_paused", "is_game_over", "is_victory", "pellets_progress"
        ]
        for key in required_keys:
            assert key in status, f"Missing key: {key}"


class TestGameStateRepr:
    """Test string representation."""

    def test_repr_format(self) -> None:
        """Test __repr__ returns valid string."""
        state = GameState()
        repr_str = repr(state)
        assert "GameState" in repr_str
        assert "score=" in repr_str
        assert "lives=" in repr_str
