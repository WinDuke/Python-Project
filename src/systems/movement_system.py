"""Movement and collision system."""

from typing import TYPE_CHECKING, List, Tuple

from src.core.constants import DIRECTIONS
from src.core.event_bus import GameEvent, EventBus

if TYPE_CHECKING:
    from src.ecs.entity_manager import EntityManager


class MovementSystem:
    """Handles entity movement, collision detection, and path validation."""

    def __init__(self, entity_manager: "EntityManager", event_bus: EventBus):
        self.em = entity_manager
        self.event_bus = event_bus
        self._solid_tiles: set[tuple[int, int]] = set()

    def set_solid_tiles(self, tiles: set[tuple[int, int]]) -> None:
        """Set the collection of solid/blocked tile positions."""
        self._solid_tiles = tiles

    def is_tile_solid(self, x: int, y: int) -> bool:
        """Check if a tile position is solid/blocked."""
        return (x, y) in self._solid_tiles

    def can_move_to(self, entity_id: int, x: int, y: int) -> bool:
        """Check if an entity can move to a position."""
        from src.components import Movement, Position

        # Check if tile is solid
        if self.is_tile_solid(x, y):
            return False

        # Check for other entities at position
        positions = self.em.query(Position)
        for other_id in positions:
            if other_id == entity_id:
                continue
            pos = self.em.get_component(other_id, Position)
            if pos and pos.x == x and pos.y == y:
                # Check if either entity can pass through
                my_movement = self.em.get_component(entity_id, Movement)
                their_movement = self.em.get_component(other_id, Movement)
                
                can_pass = False
                if my_movement and my_movement.can_pass_through:
                    can_pass = True
                if their_movement and their_movement.can_pass_through:
                    can_pass = True
                    
                if not can_pass:
                    return False

        return True

    def move_entity(self, entity_id: int, dx: int, dy: int) -> bool:
        """Move an entity by offset. Returns True if successful."""
        from src.components import Movement, Position

        position = self.em.get_component(entity_id, Position)
        if not position:
            return False

        # Check if immobilized
        movement = self.em.get_component(entity_id, Movement)
        if movement and movement.immobilized:
            return False

        new_x, new_y = position.offset(dx, dy)

        if not self.can_move_to(entity_id, new_x, new_y):
            return False

        old_x, old_y = position.x, position.y
        position.set(new_x, new_y)

        self.event_bus.emit(
            GameEvent(
                event_type="move",
                source=entity_id,
                data={"from": (old_x, old_y), "to": (new_x, new_y)},
            )
        )

        return True

    def move_to_position(self, entity_id: int, x: int, y: int) -> bool:
        """Move an entity to an absolute position. Returns True if successful."""
        from src.components import Position

        position = self.em.get_component(entity_id, Position)
        if not position:
            return False

        if not self.can_move_to(entity_id, x, y):
            return False

        old_x, old_y = position.x, position.y
        position.set(x, y)

        self.event_bus.emit(
            GameEvent(
                event_type="move",
                source=entity_id,
                data={"from": (old_x, old_y), "to": (x, y)},
            )
        )

        return True

    def get_entities_at(self, x: int, y: int) -> List[int]:
        """Get all entities at a specific position."""
        from src.components import Position

        entities = []
        positions = self.em.query(Position)
        for entity_id in positions:
            pos = self.em.get_component(entity_id, Position)
            if pos and pos.x == x and pos.y == y:
                entities.append(entity_id)
        return entities

    def get_distance(self, entity_a: int, entity_b: int) -> float:
        """Calculate distance between two entities."""
        from src.components import Position

        pos_a = self.em.get_component(entity_a, Position)
        pos_b = self.em.get_component(entity_b, Position)

        if not pos_a or not pos_b:
            return float("inf")

        dx = pos_b.x - pos_a.x
        dy = pos_b.y - pos_a.y
        return (dx * dx + dy * dy) ** 0.5

    def get_manhattan_distance(self, entity_a: int, entity_b: int) -> int:
        """Calculate Manhattan distance between two entities."""
        from src.components import Position

        pos_a = self.em.get_component(entity_a, Position)
        pos_b = self.em.get_component(entity_b, Position)

        if not pos_a or not pos_b:
            return 999999

        return abs(pos_b.x - pos_a.x) + abs(pos_b.y - pos_a.y)

    def get_direction_toward(
        self, from_entity: int, to_entity: int
    ) -> Tuple[int, int]:
        """Get the direction vector from one entity toward another."""
        from src.components import Position

        pos_from = self.em.get_component(from_entity, Position)
        pos_to = self.em.get_component(to_entity, Position)

        if not pos_from or not pos_to:
            return (0, 0)

        dx = pos_to.x - pos_from.x
        dy = pos_to.y - pos_from.y

        # Normalize to single step
        if dx != 0:
            dx = 1 if dx > 0 else -1
        if dy != 0:
            dy = 1 if dy > 0 else -1

        return (dx, dy)

    def get_neighbors(
        self, x: int, y: int, include_diagonal: bool = True
    ) -> List[Tuple[int, int]]:
        """Get valid neighboring positions."""
        neighbors = []

        directions = list(DIRECTIONS.values()) if include_diagonal else list(DIRECTIONS.values())[:4]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not self.is_tile_solid(nx, ny):
                neighbors.append((nx, ny))

        return neighbors
