"""Renderer abstraction used by the UI layer."""

from __future__ import annotations

from importlib import import_module
import os
from typing import Any, Optional, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Renderer:
    """Minimal renderer wrapper with pygame backend and headless fallback."""

    def __init__(
        self,
        width: int,
        height: int,
        title: str = "Pac-Man",
    ) -> None:
        self.width = width
        self.height = height
        self.title = title
        self._pygame: Optional[Any] = None
        self.screen: Optional[Any] = None
        self._font: Optional[Any] = None
        self._fonts: dict[tuple[str, int, bool], Any] = {}
        self._backend = "headless"

        try:
            os.environ.setdefault("SDL_RENDER_DRIVER", "software")
            self._pygame = import_module("pygame")
        except ImportError as error:
            self._pygame = None
            self.screen = None
            self._font = None
            self._backend = "headless"
            logger.warning(
                "Unable to start pygame backend (%s), running headless",
                error,
            )
            return

        pygame_error = getattr(self._pygame, "error", RuntimeError)

        try:
            self._pygame.init()
            self._pygame.font.init()
            self.screen = self._pygame.display.set_mode((width, height))
            self._pygame.display.set_caption(title)
            self._font = self._pygame.font.SysFont("Arial", 20)
            self._backend = "pygame"
            logger.info("Using pygame backend")
        except (
            AttributeError,
            OSError,
            RuntimeError,
            pygame_error,
        ) as error:  # type: ignore[misc]
            self._pygame = None
            self.screen = None
            self._font = None
            self._backend = "headless"
            logger.warning(
                "Unable to start pygame backend (%s), running headless",
                error,
            )

    def _get_font(
        self, font_name: str, size: int, bold: bool = False
    ) -> Optional[Any]:
        """Get or load a font from the font cache."""
        if self._pygame is None:
            return None
        key = (font_name, size, bold)
        if key not in self._fonts:
            try:
                self._fonts[key] = self._pygame.font.SysFont(
                    font_name, size, bold=bold
                )
            except Exception:
                try:
                    self._fonts[key] = self._pygame.font.SysFont(
                        "Arial", size, bold=bold
                    )
                except Exception:
                    return self._font
        return self._fonts[key]

    def is_headless(self) -> bool:
        """Return whether the renderer has no graphical backend."""
        return self._backend == "headless"

    def clear(self, color: Tuple[int, int, int]) -> None:
        """Clear the screen or no-op in headless mode."""
        if self.screen is not None:
            self.screen.fill(color)

    def present(self) -> None:
        """Present the current frame or no-op in headless mode."""
        if self.screen is not None and self._pygame is not None:
            self._pygame.display.update()

    def close(self) -> None:
        """Close the renderer if a backend is available."""
        if self._backend == "pygame" and self._pygame is not None:
            self._pygame.quit()

    def draw_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Draw one pixel when supported by the active backend."""
        if self.screen is None:
            return
        if 0 <= x < self.width and 0 <= y < self.height:
            self.screen.set_at((int(x), int(y)), color)

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
        if self.screen is None or self._pygame is None:
            return
        self._pygame.draw.rect(
            self.screen,
            color,
            self._pygame.Rect(int(x), int(y), int(width), int(height)),
        )

    def draw_transparent_overlay(
        self, color_with_alpha: Tuple[int, int, int, int]
    ) -> None:
        """Draw a full-screen semi-transparent overlay."""
        if self.screen is None or self._pygame is None:
            return
        overlay = self._pygame.Surface(
            (self.width, self.height), self._pygame.SRCALPHA
        )
        overlay.fill(color_with_alpha)
        self.screen.blit(overlay, (0, 0))

    def draw_text(
        self,
        x: int,
        y: int,
        text: str,
        color: Tuple[int, int, int],
        size: int = 20,
        font_name: str = "Arial",
        bold: bool = False,
    ) -> None:
        """Draw text when backend supports it."""
        if self.screen is None:
            return
        font = self._get_font(font_name, size, bold)
        if font is None:
            return
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (int(x), int(y)))

    def draw_circle(
        self,
        x: int,
        y: int,
        radius: int,
        color: Tuple[int, int, int],
        width: int = 0,
    ) -> None:
        """Draw a circle when backend supports it."""
        if radius <= 0:
            return
        if self.screen is None or self._pygame is None:
            return
        self._pygame.draw.circle(
            self.screen,
            color,
            (int(x), int(y)),
            int(radius),
            int(width),
        )

    def draw_polygon(
        self,
        points: list[tuple[int, int]],
        color: Tuple[int, int, int],
        width: int = 0,
    ) -> None:
        """Draw a polygon when backend supports it."""
        if len(points) < 3:
            return
        if self.screen is None or self._pygame is None:
            return
        self._pygame.draw.polygon(
            self.screen,
            color,
            [(int(px), int(py)) for px, py in points],
            int(width),
        )

    def draw_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: Tuple[int, int, int],
        width: int = 1,
    ) -> None:
        """Draw a line when backend supports it."""
        if width <= 0:
            return
        if self.screen is None or self._pygame is None:
            return
        self._pygame.draw.line(
            self.screen,
            color,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            int(width),
        )
