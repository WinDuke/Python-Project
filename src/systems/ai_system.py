"""AI system for enemy behavior."""

from typing import TYPE_CHECKING, Optional

from src.core.event_bus import GameEvent, EventBus
from src.ai.pathfinding import PathFinder
from src.ai.utility_ai import ActionScore, UtilityAI, create_default_scorers

if TYPE_CHECKING:
    from src.ecs.entity_manager import EntityManager
    from src.systems.movement_system import MovementSystem
    from src.systems.combat_system import CombatSystem


class AISystem:
    """Handles AI decision making and action execution."""

    def __init__(
        self,
        entity_manager: "EntityManager",
        event_bus: EventBus,
        movement_system: "MovementSystem",
        combat_system: "CombatSystem",
    ):
        self.em = entity_manager
        self.event_bus = event_bus
        self.movement = movement_system
        self.combat = combat_system
        self.utility_ai = UtilityAI(entity_manager)
        self._pathfinder: Optional[PathFinder] = None

        # Register default scorers
        scorers = create_default_scorers(movement_system, combat_system)
        for action_type, scorer in scorers.items():
            self.utility_ai.register_scorer(action_type, scorer)

    def set_pathfinder(self, pathfinder: PathFinder) -> None:
        """Set the pathfinder instance."""
        self._pathfinder = pathfinder

    def update_entity(self, entity_id: int) -> None:
        """Process AI decision and action for an entity."""
        from src.components import AI, Cooldowns

        ai = self.em.get_component(entity_id, AI)
        if not ai:
            return

        # Select best action
        action = self.utility_ai.select_action(entity_id)
        if not action:
            return

        # Execute action
        if action.action == "move":
            self._execute_move(entity_id, action)
        elif action.action == "attack":
            self._execute_attack(entity_id, action)
        elif action.action == "skill":
            self._execute_skill(entity_id, action)
        elif action.action == "retreat":
            self._execute_retreat(entity_id, action)

        # Tick cooldowns
        cooldowns = self.em.get_component(entity_id, Cooldowns)
        if cooldowns:
            cooldowns.tick()

    def _execute_move(self, entity_id: int, action: ActionScore) -> None:
        """Execute move action."""
        dx = action.data.get("dx", 0)
        dy = action.data.get("dy", 0)

        if self._pathfinder and action.target:
            # Use pathfinding for smarter movement
            target_pos = self.em.get_component(action.target, type(self.em).components.Position if hasattr(type(self.em), 'components') else type(__import__('src.components', fromlist=['Position']).Position))
            if target_pos:
                from src.components import Position
                pos = self.em.get_component(entity_id, Position)
                if pos:
                    path = self._pathfinder.find_path_to_adjacent(
                        (pos.x, pos.y),
                        (target_pos.x, target_pos.y)
                    )
                    if path and len(path) > 1:
                        next_step = path[1]  # Skip current position
                        dx = next_step[0] - pos.x
                        dy = next_step[1] - pos.y

        self.movement.move_entity(entity_id, dx, dy)

    def _execute_attack(self, entity_id: int, action: ActionScore) -> None:
        """Execute attack action."""
        if not action.target:
            return

        from src.components import Stats

        stats = self.em.get_component(entity_id, Stats)
        base_damage = stats.power if stats else 5

        self.combat.deal_damage(entity_id, action.target, base_damage)

    def _execute_skill(self, entity_id: int, action: ActionScore) -> None:
        """Execute skill action."""
        # Skills are handled by the skill system
        pass

    def _execute_retreat(self, entity_id: int, action: ActionScore) -> None:
        """Execute retreat action."""
        dx = action.data.get("dx", 0)
        dy = action.data.get("dy", 0)
        self.movement.move_entity(entity_id, dx, dy)

    def find_target(
        self, entity_id: int, max_range: float = 15.0
    ) -> Optional[int]:
        """Find the closest valid target for an entity."""
        from src.components import Faction, Position

        faction = self.em.get_component(entity_id, Faction)
        position = self.em.get_component(entity_id, Position)

        if not faction or not position:
            return None

        closest_target: Optional[int] = None
        closest_distance = max_range

        # Query all entities with Position and Faction
        candidates = self.em.query(Position, Faction)
        for candidate_id in candidates:
            if candidate_id == entity_id:
                continue

            other_faction = self.em.get_component(candidate_id, Faction)
            if not other_faction:
                continue

            # Check if hostile
            if other_faction.faction_id == faction.faction_id:
                continue

            # Calculate distance
            distance = self.movement.get_distance(entity_id, candidate_id)
            if distance < closest_distance:
                closest_distance = distance
                closest_target = candidate_id

        return closest_target

    def update_all_enemies(self) -> None:
        """Update all enemy entities."""
        from src.components import AI, Faction

        # Get all enemy entities
        enemies = self.em.query(AI, Faction)
        for entity_id in enemies:
            faction = self.em.get_component(entity_id, Faction)
            if faction and faction.faction_id != 0:  # Not player faction
                # Find/update target
                ai = self.em.get_component(entity_id, AI)
                if ai and not ai.target_entity:
                    ai.target_entity = self.find_target(entity_id)

                if ai and ai.target_entity:
                    # Verify target still exists
                    if not self.em.has_component(ai.target_entity, type(self.em).components.Position if hasattr(type(self.em), 'components') else type(__import__('src.components', fromlist=['Position']).Position)):
                        ai.target_entity = None
                    else:
                        self.update_entity(entity_id)
