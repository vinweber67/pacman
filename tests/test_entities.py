"""Tests for phase 2 entities and collisions."""

from src.entities.ghost import Ghost, GhostType
from src.entities.pacman import Pacman
from src.entities.pellet import Pellet
from src.game.collision import CollisionDetector
from src.utils.constants import Direction


class TestPacman:
    """Test Pacman behavior."""

    def test_creation(self) -> None:
        """Pacman starts at the given coordinates."""
        pacman = Pacman(10, 10)
        assert pacman.x == 10
        assert pacman.y == 10
        assert pacman.position == (10, 10)
        assert pacman.direction == Direction.NONE

    def test_move(self) -> None:
        """Pacman can move by a delta."""
        pacman = Pacman(10, 10)
        pacman.move(1, -1)
        assert pacman.position == (11, 9)

    def test_direction_queue(self) -> None:
        """Pacman applies the queued direction on update."""
        pacman = Pacman(0, 0)
        pacman.set_direction(Direction.RIGHT)
        pacman.update(0.016)
        assert pacman.direction == Direction.RIGHT
        assert pacman.next_direction == Direction.NONE


class TestGhost:
    """Test Ghost behavior."""

    def test_creation(self) -> None:
        """Ghost stores its type and spawn position."""
        ghost = Ghost(GhostType.BLINKY, 1, 2)
        assert ghost.position == (1, 2)
        assert ghost.spawn_x == 1
        assert ghost.spawn_y == 2
        assert ghost.is_edible is False

    def test_become_edible(self) -> None:
        """Ghost can become edible."""
        ghost = Ghost(GhostType.PINKY, 1, 2)
        ghost.become_edible(5.0)
        assert ghost.is_edible is True
        assert ghost.edible_timer == 5.0

    def test_respawn(self) -> None:
        """Ghost respawns on its spawn point."""
        ghost = Ghost(GhostType.INKY, 1, 2)
        ghost.move_to(7, 8)
        ghost.become_edible(2.0)
        ghost.respawn()
        assert ghost.position == (1, 2)
        assert ghost.is_edible is False
        assert ghost.edible_timer == 0.0


class TestPellet:
    """Test Pellet behavior."""

    def test_regular_pellet(self) -> None:
        """Regular pellet uses default score."""
        pellet = Pellet(3, 4)
        assert pellet.position == (3, 4)
        assert pellet.is_super is False
        assert pellet.points == 10
        assert pellet.is_eaten is False

    def test_super_pellet(self) -> None:
        """Super pellet uses higher score."""
        pellet = Pellet(3, 4, is_super=True)
        assert pellet.points == 50

    def test_eat_once_only(self) -> None:
        """Pellet can only be eaten once."""
        pellet = Pellet(3, 4)
        assert pellet.eat() == 10
        assert pellet.is_eaten is True
        assert pellet.eat() == 0


class TestCollisionDetector:
    """Test collision helpers."""

    def test_pacman_ghost_collision(self) -> None:
        """Collision is detected when positions match."""
        pacman = Pacman(5, 5)
        ghost = Ghost(GhostType.CLYDE, 5, 5)
        result = CollisionDetector.check_pacman_ghost_collision(
            pacman,
            [ghost],
        )
        assert result is ghost

    def test_pacman_ghost_no_collision(self) -> None:
        """No collision returns None."""
        pacman = Pacman(5, 5)
        ghost = Ghost(GhostType.CLYDE, 6, 6)
        result = CollisionDetector.check_pacman_ghost_collision(
            pacman,
            [ghost],
        )
        assert result is None

    def test_pacman_pellet_collision(self) -> None:
        """Pellet collision is detected when positions match."""
        pacman = Pacman(2, 2)
        pellet = Pellet(2, 2)
        result = CollisionDetector.check_pacman_pellet_collision(
            pacman,
            [pellet],
        )
        assert result is pellet

    def test_pacman_pellet_ignores_eaten(self) -> None:
        """Already eaten pellets are ignored."""
        pacman = Pacman(2, 2)
        pellet = Pellet(2, 2)
        pellet.eat()
        result = CollisionDetector.check_pacman_pellet_collision(
            pacman,
            [pellet],
        )
        assert result is None
