"""Render system with dirty tile optimization."""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from rich.style import Style
from rich.text import Text


@dataclass
class Tile:
    """Represents a single renderable tile."""
    symbol: str = " "
    style: Style | None = None
    bg_style: Style | None = None


@dataclass
class RenderLayer:
    """A single render layer."""
    name: str
    priority: int
    tiles: Dict[Tuple[int, int], Tile] = field(default_factory=dict)


class TerminalBuffer:
    """Double-buffered terminal rendering with dirty tile tracking."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._current_buffer: Dict[Tuple[int, int], Tile] = {}
        self._previous_buffer: Dict[Tuple[int, int], Tile] = {}
        self._dirty_tiles: set[Tuple[int, int]] = set()

    def set_tile(
        self,
        x: int, y: int,
        symbol: str,
        style: Style | None = None,
        bg_style: Style | None = None,
    ) -> None:
        """Set a tile and mark it as dirty if changed."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        old_tile = self._current_buffer.get((x, y))
        new_tile = Tile(symbol=symbol, style=style, bg_style=bg_style)

        # Check if tile actually changed
        if old_tile is None or (
            old_tile.symbol != new_tile.symbol
            or old_tile.style != new_tile.style
            or old_tile.bg_style != new_tile.bg_style
        ):
            self._current_buffer[(x, y)] = new_tile
            self._dirty_tiles.add((x, y))

    def clear(self) -> None:
        """Clear the buffer."""
        self._current_buffer.clear()
        self._dirty_tiles = set(range(self.width) for _ in range(self.height))
        # Flatten the set of sets
        self._dirty_tiles = {(x, y) for x in range(self.width) for y in range(self.height)}

    def swap_buffers(self) -> None:
        """Swap buffers and return dirty tiles."""
        self._previous_buffer = self._current_buffer.copy()
        dirty = self._dirty_tiles.copy()
        self._dirty_tiles.clear()
        return dirty

    def get_dirty_tiles(self) -> set[Tuple[int, int]]:
        """Get current dirty tiles."""
        return self._dirty_tiles.copy()

    def is_dirty(self, x: int, y: int) -> bool:
        """Check if a specific tile is dirty."""
        return (x, y) in self._dirty_tiles

    def mark_dirty(self, x: int, y: int) -> None:
        """Manually mark a tile as dirty."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self._dirty_tiles.add((x, y))

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at position."""
        return self._current_buffer.get((x, y))


class RenderSystem:
    """Main rendering system with layered rendering."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.buffer = TerminalBuffer(width, height)
        self._layers: Dict[str, RenderLayer] = {}
        self._camera_x = 0
        self._camera_y = 0

    def register_layer(self, name: str, priority: int = 0) -> None:
        """Register a render layer."""
        self._layers[name] = RenderLayer(name=name, priority=priority)

    def get_layer(self, name: str) -> Optional[RenderLayer]:
        """Get a render layer by name."""
        return self._layers.get(name)

    def set_tile(
        self,
        layer_name: str,
        x: int, y: int,
        symbol: str,
        color: str = "white",
        bold: bool = False,
        dim: bool = False,
        blink: bool = False,
        bg_color: str | None = None,
    ) -> None:
        """Set a tile on a specific layer."""
        layer = self._layers.get(layer_name)
        if not layer:
            return

        # Create Rich style
        style_parts = []
        if color:
            style_parts.append(color)
        if bold:
            style_parts.append("bold")
        if dim:
            style_parts.append("dim")
        if blink:
            style_parts.append("blink")

        style = Style.parse(" ".join(style_parts)) if style_parts else None
        bg_style = Style.parse(f"on {bg_color}") if bg_color else None

        # Store in layer
        layer.tiles[(x, y)] = Tile(symbol=symbol, style=style, bg_style=bg_style)

    def clear_layer(self, layer_name: str) -> None:
        """Clear all tiles from a layer."""
        layer = self._layers.get(layer_name)
        if layer:
            layer.tiles.clear()

    def render(self) -> Text:
        """Render all layers to the buffer and return Rich Text."""
        from src.core.constants import (
            LAYER_TERRAIN, LAYER_OBJECTS, LAYER_UNITS,
            LAYER_EFFECTS, LAYER_PARTICLES
        )

        # Sort layers by priority
        sorted_layers = sorted(
            self._layers.values(),
            key=lambda l: l.priority
        )

        # Clear buffer
        self.buffer._current_buffer.clear()
        self.buffer._dirty_tiles = set()

        # Render each layer
        for layer in sorted_layers:
            for (x, y), tile in layer.tiles.items():
                # Apply camera offset
                screen_x = x - self._camera_x
                screen_y = y - self._camera_y

                if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                    self.buffer.set_tile(
                        screen_x, screen_y,
                        tile.symbol,
                        tile.style,
                        tile.bg_style
                    )

        return self._build_rich_text()

    def _build_rich_text(self) -> Text:
        """Build Rich Text from buffer."""
        text = Text()

        for y in range(self.height):
            for x in range(self.width):
                tile = self.buffer.get_tile(x, y)
                if tile:
                    styled_text = Text(tile.symbol, style=tile.style)
                    if tile.bg_style:
                        styled_text.stylize(tile.bg_style)
                    text.append(styled_text)
                else:
                    text.append(" ")

            if y < self.height - 1:
                text.append("\n")

        return text

    def set_camera(self, x: int, y: int) -> None:
        """Set camera position."""
        self._camera_x = x
        self._camera_y = y

    def center_camera_on(self, x: int, y: int) -> None:
        """Center camera on a position."""
        self._camera_x = max(0, min(x - self.width // 2, self.width))
        self._camera_y = max(0, min(y - self.height // 2, self.height))
