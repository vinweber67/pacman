"""Tests for configuration loading and validation."""

import json
import tempfile
from pathlib import Path

import pytest

from src.config.config_loader import ConfigLoader
from src.config.config_validator import ConfigValidator
from src.utils.exceptions import ConfigError


class TestConfigLoader:
    """Test ConfigLoader class."""

    def test_load_valid_config(self) -> None:
        """Test loading valid config without comments."""
        config_data = {"lives": 5, "points_per_pacgum": 20}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config_data, f)
            f.flush()

            config = ConfigLoader.load(f.name)
            assert config["lives"] == 5
            assert config["points_per_pacgum"] == 20

            Path(f.name).unlink()

    def test_load_config_with_cpp_comments(self) -> None:
        """Test loading config with C++ style comments."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("""
            {
              // Comment style C++
              "lives": 5,  // Lives count
              "points_per_pacgum": 10  // Points
            }
            """)
            f.flush()

            config = ConfigLoader.load(f.name)
            assert config["lives"] == 5
            assert config["points_per_pacgum"] == 10

            Path(f.name).unlink()

    def test_load_config_with_python_comments(self) -> None:
        """Test loading config with Python style comments."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("""
            {
              # Python style comment
              "lives": 5,
              "points_per_pacgum": 10  # Another comment
            }
            """)
            f.flush()

            config = ConfigLoader.load(f.name)
            assert config["lives"] == 5
            assert config["points_per_pacgum"] == 10

            Path(f.name).unlink()

    def test_load_config_file_not_found(self) -> None:
        """Test error when file not found."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load("nonexistent_file.json")

    def test_load_config_invalid_json(self) -> None:
        """Test error for invalid JSON."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("{invalid json}")
            f.flush()

            with pytest.raises(ConfigError):
                ConfigLoader.load(f.name)

            Path(f.name).unlink()

    def test_remove_comments(self) -> None:
        """Test comment removal."""
        content = """
        {
          // C++ comment
          "key": "value",  // inline comment
          # Python comment
          "key2": "value2"  # inline
        }
        """
        cleaned = ConfigLoader._remove_comments(content)
        assert "//" not in cleaned
        assert "#" not in cleaned


class TestConfigValidator:
    """Test ConfigValidator class."""

    def test_validate_applies_defaults(self) -> None:
        """Test validation applies defaults."""
        config = {"lives": 5}
        validated = ConfigValidator.validate(config)

        assert validated["lives"] == 5
        assert validated["points_per_pacgum"] == 10
        assert len(validated["levels"]) > 0

    def test_validate_invalid_type(self) -> None:
        """Test validation with invalid type."""
        config = "not a dict"  # type: ignore
        validated = ConfigValidator.validate(config)

        # Should use defaults
        assert validated["lives"] == 3
        assert len(validated["levels"]) > 0

    def test_validate_invalid_lives(self) -> None:
        """Test validation with invalid lives."""
        config = {"lives": -1}
        validated = ConfigValidator.validate(config)

        assert validated["lives"] == 3  # Default

    def test_validate_invalid_points(self) -> None:
        """Test validation with invalid points."""
        config = {"points_per_pacgum": -10}
        validated = ConfigValidator.validate(config)

        assert validated["points_per_pacgum"] == 10  # Default

    def test_validate_invalid_levels(self) -> None:
        """Test validation with invalid levels."""
        config = {"levels": []}
        validated = ConfigValidator.validate(config)

        assert len(validated["levels"]) > 0  # Default

    def test_validate_level_with_missing_keys(self) -> None:
        """Test level validation with missing keys."""
        level = {"width": 21, "height": 21}  # Missing seed and max_time
        result = ConfigValidator._validate_level(level)

        assert result is False

    def test_validate_level_with_invalid_size(self) -> None:
        """Test level validation with invalid size."""
        level = {"width": 2, "height": 2, "seed": 42, "max_time": 90}
        result = ConfigValidator._validate_level(level)

        assert result is False

    def test_validate_level_valid(self) -> None:
        """Test valid level."""
        level = {"width": 21, "height": 21, "seed": 42, "max_time": 90}
        result = ConfigValidator._validate_level(level)

        assert result is True
