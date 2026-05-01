"""Renderer abstraction used by the UI layer."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Optional, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Renderer:
    """Minimal renderer wrapper with optional MLX42 backend."""

    def __init__(
        self,
        width: int,
        height: int,
        title: str = "Pac-Man",
    ) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.mlx: Optional[Any]

        try:
            mlx_module = import_module("MLX42")
            mlx_class = getattr(mlx_module, "MLX42")
            self.mlx = mlx_class(width, height, title)
        except Exception:
            self.mlx = None
            logger.warning("MLX42 unavailable, running in headless mode")

    def clear(self, color: Tuple[int, int, int]) -> None:
        """Clear the screen or no-op in headless mode."""
        if self.mlx is not None:
            self.mlx.clear_background(color)

    def present(self) -> None:
        """Present the current frame or no-op in headless mode."""
        if self.mlx is not None:
            self.mlx.do_loop()

    def close(self) -> None:
        """Close the renderer if a backend is available."""
        if self.mlx is not None:
            self.mlx.terminate()
