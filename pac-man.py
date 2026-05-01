#!/usr/bin/env python3
"""
Pac-Man Game - Main Entry Point

Usage:
    python3 pac-man.py <config.json>
"""

import sys
from pathlib import Path

from src.utils.logger import setup_logger
from src.utils.exceptions import ConfigError, PacmanError

# Setup logger for main
logger = setup_logger(__name__)


def main() -> int:
    """
    Main entry point for Pac-Man game.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Check command line arguments
    if len(sys.argv) != 2:
        logger.error("Usage: python3 pac-man.py <config.json>")
        return 1

    config_path = sys.argv[1]

    # Validate that config file exists
    if not Path(config_path).exists():
        logger.error(f"Config file not found: {config_path}")
        return 1

    # Validate that it's a JSON file
    if not config_path.endswith(".json"):
        logger.error(f"Config file must be JSON: {config_path}")
        return 1

    try:
        # Import here to avoid issues if config loading fails
        from src.config.config_loader import ConfigLoader
        from src.config.config_validator import ConfigValidator
        from src.game.game_manager import GameManager

        # Load and validate configuration
        logger.info(f"Loading config from: {config_path}")
        config = ConfigLoader.load(config_path)
        config = ConfigValidator.validate(config)
        logger.info("Config loaded and validated successfully")

        # Initialize and run game
        logger.info("Initializing game manager...")
        game = GameManager(config)

        logger.info("Starting game...")
        game.run()

    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except PacmanError as e:
        logger.error(f"Game error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1

    logger.info("Game ended normally")
    return 0


if __name__ == "__main__":
    sys.exit(main())
