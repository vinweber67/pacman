"""Renderer abstraction used by the UI layer."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Optional, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Renderer:
    """Minimal renderer wrapper with optional MLX backend."""

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
        self._backend = "headless"
        self._mlx_ptr: Optional[Any] = None
        self._win_ptr: Optional[Any] = None

        try:
            mlx_module = import_module("MLX42")
            mlx_class = getattr(mlx_module, "MLX42")
            self.mlx = mlx_class(width, height, title)
            self._backend = "mlx42"
            return
        except Exception:
            logger.info("MLX42 unavailable, trying mlx wheel backend")

        try:
            mlx_module = import_module("mlx")
            mlx_class = getattr(mlx_module, "Mlx")
            mlx_instance = mlx_class()
            mlx_ptr = mlx_instance.mlx_init()
            if mlx_ptr is None:
                raise RuntimeError("mlx_init returned NULL")

            win_ptr = mlx_instance.mlx_new_window(
                mlx_ptr,
                width,
                height,
                title,
            )
            if win_ptr is None:
                raise RuntimeError("mlx_new_window returned NULL")

            self.mlx = mlx_instance
            self._mlx_ptr = mlx_ptr
            self._win_ptr = win_ptr
            self._backend = "mlx"
            logger.info("Using mlx wheel backend")
        except Exception:
            self.mlx = None
            self._mlx_ptr = None
            self._win_ptr = None
            self._backend = "headless"
            logger.warning(
                "No graphics backend available, running in headless mode"
            )

    def clear(self, color: Tuple[int, int, int]) -> None:
        """Clear the screen or no-op in headless mode."""
        if self.mlx is None:
            return

        if self._backend == "mlx42":
            self.mlx.clear_background(color)
            return

        if self._backend == "mlx" and self._mlx_ptr and self._win_ptr:
            self.mlx.mlx_clear_window(self._mlx_ptr, self._win_ptr)

    def present(self) -> None:
        """Present the current frame or no-op in headless mode."""
        if self.mlx is None:
            return

        if self._backend == "mlx42":
            self.mlx.do_loop()
            return

        if self._backend == "mlx" and self._mlx_ptr:
            self.mlx.mlx_do_sync(self._mlx_ptr)

    def close(self) -> None:
        """Close the renderer if a backend is available."""
        if self.mlx is None:
            return

        if self._backend == "mlx42":
            self.mlx.terminate()
            return

        if self._backend == "mlx" and self._mlx_ptr and self._win_ptr:
            self.mlx.mlx_destroy_window(self._mlx_ptr, self._win_ptr)
            self.mlx.mlx_release(self._mlx_ptr)

    def draw_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Draw one pixel when supported by the active backend."""
        if self.mlx is None:
            return
        if self._backend == "mlx" and self._mlx_ptr and self._win_ptr:
            rgb_color = self._to_rgb_int(color)
            self.mlx.mlx_pixel_put(
                self._mlx_ptr,
                self._win_ptr,
                int(x),
                int(y),
                rgb_color,
            )

    def draw_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int],
    ) -> None:
        """Draw a filled rectangle using repeated pixel writes."""
        if width <= 0 or height <= 0:
            return
        for py in range(y, y + height):
            for px in range(x, x + width):
                self.draw_pixel(px, py, color)

    def draw_text(
        self,
        x: int,
        y: int,
        text: str,
        color: Tuple[int, int, int],
    ) -> None:
        """Draw text when backend supports it."""
        if self.mlx is None:
            return
        if self._backend == "mlx" and self._mlx_ptr and self._win_ptr:
            rgb_color = self._to_rgb_int(color)
            self.mlx.mlx_string_put(
                self._mlx_ptr,
                self._win_ptr,
                int(x),
                int(y),
                rgb_color,
                text,
            )

    @staticmethod
    def _to_rgb_int(color: Tuple[int, int, int]) -> int:
        """Convert an RGB tuple to integer format expected by mlx."""
        red, green, blue = color
        return ((red & 0xFF) << 16) | ((green & 0xFF) << 8) | (blue & 0xFF)
