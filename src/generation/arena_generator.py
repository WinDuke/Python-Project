"""Procedural arena generation."""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple


@dataclass
class Arena:
    """Represents a generated arena."""
    width: int
    height: int
    tiles: Dict[Tuple[int, int], str] = field(default_factory=dict)
    obstacles: Set[Tuple[int, int]] = field(default_factory=set)
    spawn_points: List[Tuple[int, int]] = field(default_factory=list)
    player_start: Tuple[int, int] = (0, 0)
    biome: str = "cemetery"
    hazards: Set[Tuple[int, int]] = field(default_factory=set)


class ArenaGenerator:
    """Generates procedural arenas for combat."""

    def __init__(self, width: int = 50, height: int = 25):
        self.width = width
        self.height = height
        self._rng = random.Random()

    def generate(
        self,
        biome: str = "cemetery",
        obstacle_density: float = 0.15,
        seed: int | None = None,
    ) -> Arena:
        """Generate a new arena."""
        if seed is not None:
            self._rng.seed(seed)

        arena = Arena(width=self.width, height=self.height, biome=biome)

        # Fill with floor tiles
        for x in range(self.width):
            for y in range(self.height):
                arena.tiles[(x, y)] = "."

        # Generate borders
        self._generate_borders(arena)

        # Generate obstacles based on biome
        self._generate_obstacles(arena, obstacle_density)

        # Generate spawn points
        self._generate_spawn_points(arena)

        # Set player start position
        arena.player_start = self._find_player_start(arena)

        return arena

    def _generate_borders(self, arena: Arena) -> None:
        """Generate arena borders."""
        for x in range(self.width):
            arena.tiles[(x, 0)] = "#"
            arena.tiles[(x, self.height - 1)] = "#"
            arena.obstacles.add((x, 0))
            arena.obstacles.add((x, self.height - 1))

        for y in range(self.height):
            arena.tiles[(0, y)] = "#"
            arena.tiles[(self.width - 1, y)] = "#"
            arena.obstacles.add((0, y))
            arena.obstacles.add((self.width - 1, y))

    def _generate_obstacles(self, arena: Arena, density: float) -> None:
        """Generate obstacles based on biome."""
        interior_width = self.width - 2
        interior_height = self.height - 2

        num_obstacles = int(interior_width * interior_height * density)

        for _ in range(num_obstacles):
            x = self._rng.randint(2, self.width - 3)
            y = self._rng.randint(2, self.height - 3)

            if (x, y) not in arena.obstacles:
                arena.obstacles.add((x, y))
                arena.tiles[(x, y)] = self._get_obstacle_symbol(arena.biome)

    def _get_obstacle_symbol(self, biome: str) -> str:
        """Get obstacle symbol for biome."""
        symbols = {
            "cemetery": "▓",  # Tombstones
            "crimson_cathedral": "█",  # Pillars
            "frozen_hollow": "≈",  # Ice formations
            "void_fracture": "╬",  # Void cracks
        }
        return symbols.get(biome, "▓")

    def _generate_spawn_points(self, arena: Arena) -> None:
        """Generate enemy spawn points around arena edges."""
        # Spawn points along edges (but not corners)
        margin = 3

        # Top and bottom edges
        for x in range(margin, self.width - margin):
            arena.spawn_points.append((x, 2))
            arena.spawn_points.append((x, self.height - 3))

        # Left and right edges
        for y in range(margin, self.height - margin):
            arena.spawn_points.append((2, y))
            arena.spawn_points.append((self.width - 3, y))

        # Remove duplicates and obstacle positions
        arena.spawn_points = [
            p for p in arena.spawn_points
            if p not in arena.obstacles
        ]

    def _find_player_start(self, arena: Arena) -> Tuple[int, int]:
        """Find a suitable player starting position (center of arena)."""
        center_x = self.width // 2
        center_y = self.height // 2

        # Search outward from center for valid position
        for radius in range(min(self.width, self.height) // 2):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x = center_x + dx
                    y = center_y + dy
                    if (
                        0 <= x < self.width
                        and 0 <= y < self.height
                        and (x, y) not in arena.obstacles
                    ):
                        return (x, y)

        # Fallback to absolute center
        return (center_x, center_y)

    def get_tile(self, arena: Arena, x: int, y: int) -> str:
        """Get tile at position."""
        return arena.tiles.get((x, y), ".")

    def set_tile(self, arena: Arena, x: int, y: int, tile: str) -> None:
        """Set tile at position."""
        arena.tiles[(x, y)] = tile
        if tile == "#":
            arena.obstacles.add((x, y))
        elif (x, y) in arena.obstacles:
            arena.obstacles.discard((x, y))

    def is_valid_position(self, arena: Arena, x: int, y: int) -> bool:
        """Check if position is valid for movement."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return (x, y) not in arena.obstacles

    def get_random_empty_position(
        self, arena: Arena, avoid_radius: int = 0
    ) -> Tuple[int, int]:
        """Get a random empty position."""
        attempts = 0
        max_attempts = 100

        while attempts < max_attempts:
            x = self._rng.randint(1, self.width - 2)
            y = self._rng.randint(1, self.height - 2)

            if (x, y) not in arena.obstacles:
                if avoid_radius > 0:
                    # Check distance from all obstacles
                    too_close = False
                    for ox, oy in arena.obstacles:
                        if abs(ox - x) + abs(oy - y) <= avoid_radius:
                            too_close = True
                            break
                    if too_close:
                        attempts += 1
                        continue

                return (x, y)

            attempts += 1

        # Fallback
        return (self.width // 2, self.height // 2)
