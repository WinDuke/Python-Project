"""ECS-lite entity management system."""

from dataclasses import dataclass, field
from typing import Any, Dict, Set, Type


@dataclass
class Component:
    """Base component class - all components must inherit from this."""
    pass


class EntityManager:
    """Manages entities and their components using archetype-based storage."""

    def __init__(self):
        self._next_id = 0
        self._components: Dict[int, Dict[Type[Component], Component]] = {}
        self._archetypes: Dict[frozenset, Set[int]] = {}
        self._entity_archetype: Dict[int, frozenset] = {}

    def create_entity(self) -> int:
        """Create a new entity and return its ID."""
        entity_id = self._next_id
        self._next_id += 1
        self._components[entity_id] = {}
        self._entity_archetype[entity_id] = frozenset()
        self._archetypes.setdefault(frozenset(), set()).add(entity_id)
        return entity_id

    def destroy_entity(self, entity_id: int) -> None:
        """Destroy an entity and remove all its components."""
        if entity_id not in self._components:
            return

        archetype = self._entity_archetype.get(entity_id, frozenset())
        if archetype in self._archetypes:
            self._archetypes[archetype].discard(entity_id)

        del self._components[entity_id]
        self._entity_archetype.pop(entity_id, None)

    def add_component(self, entity_id: int, component: Component) -> None:
        """Add a component to an entity."""
        if entity_id not in self._components:
            raise ValueError(f"Entity {entity_id} does not exist")

        comp_type = type(component)
        old_components = self._components[entity_id]

        # Remove from old archetype
        old_archetype = self._entity_archetype[entity_id]
        if old_archetype in self._archetypes:
            self._archetypes[old_archetype].discard(entity_id)

        # Add component
        old_components[comp_type] = component

        # Create new archetype
        new_archetype = frozenset(old_components.keys())
        self._components[entity_id] = old_components
        self._entity_archetype[entity_id] = new_archetype
        self._archetypes.setdefault(new_archetype, set()).add(entity_id)

    def remove_component(self, entity_id: int, component_type: Type[Component]) -> None:
        """Remove a component from an entity."""
        if entity_id not in self._components:
            return

        old_components = self._components[entity_id]
        if component_type not in old_components:
            return

        # Remove from old archetype
        old_archetype = self._entity_archetype[entity_id]
        if old_archetype in self._archetypes:
            self._archetypes[old_archetype].discard(entity_id)

        # Remove component
        del old_components[component_type]

        # Create new archetype
        new_archetype = frozenset(old_components.keys())
        self._entity_archetype[entity_id] = new_archetype
        self._archetypes.setdefault(new_archetype, set()).add(entity_id)

    def get_component(self, entity_id: int, component_type: Type[Component]) -> Component | None:
        """Get a specific component from an entity."""
        if entity_id not in self._components:
            return None
        return self._components[entity_id].get(component_type)

    def has_component(self, entity_id: int, component_type: Type[Component]) -> bool:
        """Check if an entity has a specific component."""
        if entity_id not in self._components:
            return False
        return component_type in self._components[entity_id]

    def has_all_components(self, entity_id: int, component_types: list[Type[Component]]) -> bool:
        """Check if an entity has all specified components."""
        if entity_id not in self._components:
            return False
        for comp_type in component_types:
            if comp_type not in self._components[entity_id]:
                return False
        return True

    def query(self, *component_types: Type[Component]) -> list[int]:
        """Query entities that have all specified components."""
        if not component_types:
            return list(self._components.keys())

        matching_entities = []
        for archetype, entities in self._archetypes.items():
            if all(comp_type in archetype for comp_type in component_types):
                matching_entities.extend(entities)
        return matching_entities

    def get_all_entities(self) -> list[int]:
        """Get all active entity IDs."""
        return list(self._components.keys())

    def count(self) -> int:
        """Get the count of active entities."""
        return len(self._components)

    def clear(self) -> None:
        """Clear all entities and components."""
        self._components.clear()
        self._archetypes.clear()
        self._entity_archetype.clear()
        self._next_id = 0
