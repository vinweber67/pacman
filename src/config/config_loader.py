"""Configuration loader with comment support."""

import json
import re
from pathlib import Path
from typing import Any, Dict

from src.utils.logger import setup_logger
from src.utils.exceptions import ConfigError

logger = setup_logger(__name__)


class ConfigLoader:
    """Load JSON config files with comment support."""

    @staticmethod
    def load(filepath: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file with comments.

        Supports both # and // style comments.

        Args:
            filepath: Path to configuration file

        Returns:
            Dictionary containing configuration

        Raises:
            FileNotFoundError: If file doesn't exist
            ConfigError: If JSON is invalid
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except IOError as e:
            raise ConfigError(f"Failed to read config file: {e}")

        # Remove comments
        content = ConfigLoader._remove_comments(content)

        # Parse JSON
        try:
            config: Dict[str, Any] = json.loads(content)
            return config
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file: {e}")

    @staticmethod
    def _remove_comments(content: str) -> str:
        """
        Remove comments from JSON content.

        Supports both # and // style comments.

        Args:
            content: JSON content with comments

        Returns:
            JSON content without comments
        """
        # Remove // comments (C++ style)
        content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
        # Remove # comments (Python style)
        content = re.sub(r"#.*?$", "", content, flags=re.MULTILINE)
        return content
