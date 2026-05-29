"""Configuration validation and default values."""

from typing import Any, Dict

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConfigValidator:
    """Validate configuration and apply default values."""

    DEFAULT_CONFIG: Dict[str, Any] = {
        "highscore_filename": ".data/highscores.json",
        "lives": 3,
        "pacgum_count": 42,
        "pacman_move_interval": 0.28,
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "ghost_respawn_time": 10,
        "super_pacgum_duration": 10,
        "levels": [
            {"width": 21, "height": 21, "seed": 42, "max_time": 90}
        ]
    }
    SUPPORTED_KEYS: set[str] = set(DEFAULT_CONFIG.keys())

    @staticmethod
    def validate(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration and apply defaults.

        Args:
            config: Configuration dictionary

        Returns:
            Validated configuration dictionary
        """
        if not isinstance(config, dict):
            logger.warning("Config is not a dict, using defaults")
            return ConfigValidator.DEFAULT_CONFIG.copy()

        # Merge with defaults while ignoring unsupported keys.
        validated = ConfigValidator.DEFAULT_CONFIG.copy()
        for key, value in config.items():
            if key not in ConfigValidator.SUPPORTED_KEYS:
                logger.warning("Ignoring unsupported config key: %s", key)
                continue
            validated[key] = value

        # Validate values
        ConfigValidator._validate_values(validated)

        return validated

    @staticmethod
    def _validate_values(config: Dict[str, Any]) -> None:
        """
        Validate individual configuration values.

        Args:
            config: Configuration dictionary to validate
        """
        # Validate lives
        lives = config.get("lives", 3)
        if not isinstance(lives, int) or lives < 1:
            logger.warning("Invalid lives count, using default: 3")
            config["lives"] = 3
        else:
            config["lives"] = lives

        # Validate points
        for key in [
            "points_per_pacgum",
            "points_per_super_pacgum",
            "points_per_ghost"
        ]:
            points = config.get(key)
            if not isinstance(points, int) or points < 0:
                default_value = ConfigValidator.DEFAULT_CONFIG[key]
                logger.warning(
                    f"Invalid {key}, using default: {default_value}"
                )
                config[key] = default_value

        pacman_move_interval = config.get("pacman_move_interval")
        if (
            not isinstance(pacman_move_interval, (int, float))
            or pacman_move_interval <= 0
        ):
            default_value = ConfigValidator.DEFAULT_CONFIG[
                "pacman_move_interval"
            ]
            logger.warning(
                "Invalid pacman_move_interval, using default: %s",
                default_value,
            )
            config["pacman_move_interval"] = default_value

        # Validate respawn times
        for key in ["ghost_respawn_time", "super_pacgum_duration"]:
            time_val = config.get(key)
            if not isinstance(time_val, int) or time_val < 1:
                default_value = ConfigValidator.DEFAULT_CONFIG[key]
                logger.warning(
                    f"Invalid {key}, using default: {default_value}"
                )
                config[key] = default_value

        # Validate levels
        levels = config.get("levels")
        if not isinstance(levels, list) or len(levels) == 0:
            logger.warning("Invalid levels, using default")
            config["levels"] = ConfigValidator.DEFAULT_CONFIG["levels"]
        else:
            # Validate each level
            valid_levels = []
            for i, level in enumerate(levels):
                if isinstance(level, dict):
                    if ConfigValidator._validate_level(level):
                        valid_levels.append(level)
                    else:
                        logger.warning(f"Invalid level {i}, skipping")
                else:
                    logger.warning(f"Level {i} is not a dict, skipping")

            if valid_levels:
                config["levels"] = valid_levels
            else:
                logger.warning("No valid levels found, using default")
                config["levels"] = ConfigValidator.DEFAULT_CONFIG["levels"]

    @staticmethod
    def _validate_level(level: Dict[str, Any]) -> bool:
        """
        Validate a single level configuration.

        Args:
            level: Level configuration dictionary

        Returns:
            True if valid, False otherwise
        """
        required_keys = ["width", "height", "seed", "max_time"]

        for key in required_keys:
            if key not in level:
                logger.warning(f"Missing level key: {key}")
                return False

        width = level.get("width")
        height = level.get("height")
        if not isinstance(width, int) or not isinstance(height, int):
            logger.warning("Width and height must be integers")
            return False

        if width < 5 or height < 5:
            logger.warning("Width and height must be at least 5")
            return False

        return True
