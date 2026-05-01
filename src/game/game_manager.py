"""Game manager stub for Phase 0 infrastructure."""

from typing import Any, Dict

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GameManager:
    """
    Main game manager (stub for Phase 0).

    Will be fully implemented in Phase 5.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize game manager.

        Args:
            config: Game configuration
        """
        self.config = config
        logger.info("GameManager initialized")

    def run(self) -> None:
        """Run the game (stub)."""
        logger.info("Game would start here (stub implementation)")
        logger.info(f"Config: {self.config}")
