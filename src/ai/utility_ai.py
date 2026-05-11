"""Utility AI system for enemy decision making."""

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from src.ecs.entity_manager import EntityManager


@dataclass
class ActionScore:
    """Score for a potential action."""
    action: str
    score: float
    target: Optional[int] = None
    data: Dict = field(default_factory=dict)


class UtilityAI:
    """Utility-based AI decision system."""

    def __init__(self, entity_manager: "EntityManager"):
        self.em = entity_manager
        self._action_scorers: Dict[str, Callable[[int], List[ActionScore]]] = {}

    def register_scorer(
        self, action_type: str, scorer: Callable[[int], List[ActionScore]]
    ) -> None:
        """Register a scorer function for an action type."""
        self._action_scorers[action_type] = scorer

    def select_action(self, entity_id: int) -> Optional[ActionScore]:
        """
        Evaluate all possible actions and return the best one.
        """
        from src.components import AI, Health

        ai = self.em.get_component(entity_id, AI)
        health = self.em.get_component(entity_id, Health)

        if not ai:
            return None

        all_scores: List[ActionScore] = []

        # Evaluate each action type
        for action_type, scorer in self._action_scorers.items():
            try:
                scores = scorer(entity_id)
                all_scores.extend(scores)
            except Exception as e:
                print(f"Error scoring {action_type}: {e}")

        if not all_scores:
            return None

        # Apply behavior modifiers
        self._apply_behavior_modifiers(entity_id, all_scores)

        # Check retreat threshold
        if health and ai.retreat_threshold > 0:
            hp_percent = health.percent
            if hp_percent <= ai.retreat_threshold:
                # Boost retreat actions
                for score in all_scores:
                    if score.action == "retreat":
                        score.score *= 2.0

        # Select highest scored action
        best = max(all_scores, key=lambda s: s.score)

        # Only act if score is above minimum threshold
        if best.score < 0.1:
            return None

        return best

    def _apply_behavior_modifiers(
        self, entity_id: int, scores: List[ActionScore]
    ) -> None:
        """Apply behavior profile modifiers to scores."""
        from src.components import AI

        ai = self.em.get_component(entity_id, AI)
        if not ai:
            return

        # Aggression affects attack vs defensive actions
        for score in scores:
            if score.action in ("attack", "skill_attack"):
                score.score *= ai.aggression
            elif score.action in ("retreat", "defend"):
                score.score *= (1.0 - ai.aggression)

        # Behavior type modifiers
        if ai.behavior_type == "aggressive":
            for score in scores:
                if score.action == "attack":
                    score.score *= 1.3
        elif ai.behavior_type == "defensive":
            for score in scores:
                if score.action in ("defend", "retreat"):
                    score.score *= 1.3
        elif ai.behavior_type == "tactical":
            for score in scores:
                if score.action == "skill_attack":
                    score.score *= 1.2
        elif ai.behavior_type == "frenzied":
            for score in scores:
                if score.action == "attack":
                    score.score *= 1.5


# Default scorers for common enemy actions
def create_default_scorers(movement_system, combat_system):
    """Create default action scorers."""

    def score_move(entity_id: int) -> List[ActionScore]:
        """Score movement toward target."""
        from src.components import AI, Position

        ai = movement_system.em.get_component(entity_id, AI)
        position = movement_system.em.get_component(entity_id, Position)

        if not ai or not position or not ai.target_entity:
            return []

        target_pos = movement_system.em.get_component(ai.target_entity, Position)
        if not target_pos:
            return []

        distance = movement_system.get_manhattan_distance(entity_id, ai.target_entity)
        
        # Score based on distance - closer is better
        score = max(0, 1.0 - (distance / 20.0))
        
        dx, dy = movement_system.get_direction_toward(entity_id, ai.target_entity)
        
        return [ActionScore(
            action="move",
            score=score,
            target=ai.target_entity,
            data={"dx": dx, "dy": dy}
        )]

    def score_attack(entity_id: int) -> List[ActionScore]:
        """Score attack action."""
        from src.components import AI

        ai = movement_system.em.get_component(entity_id, AI)
        if not ai or not ai.target_entity:
            return []

        distance = movement_system.get_manhattan_distance(entity_id, ai.target_entity)
        
        # Can only attack at range 1
        if distance > 1:
            return []

        return [ActionScore(
            action="attack",
            score=0.8,
            target=ai.target_entity,
            data={}
        )]

    def score_skill(entity_id: int) -> List[ActionScore]:
        """Score skill usage."""
        from src.components import AI, Cooldowns

        ai = movement_system.em.get_component(entity_id, AI)
        cooldowns = movement_system.em.get_component(entity_id, Cooldowns)

        if not ai or not ai.target_entity or not cooldowns:
            return []

        scores = []
        for skill_id in ai.skills:
            if cooldowns.is_ready(skill_id):
                # Base score with some randomness
                score = 0.5 + random.random() * 0.3
                scores.append(ActionScore(
                    action="skill",
                    score=score,
                    target=ai.target_entity,
                    data={"skill_id": skill_id}
                ))

        return scores

    def score_retreat(entity_id: int) -> List[ActionScore]:
        """Score retreat action."""
        from src.components import AI, Health, Position

        ai = movement_system.em.get_component(entity_id, AI)
        health = movement_system.em.get_component(entity_id, Health)
        position = movement_system.em.get_component(entity_id, Position)

        if not ai or not health or not position or not ai.target_entity:
            return []

        # Only consider retreat when low HP
        if health.percent > ai.retreat_threshold + 0.2:
            return []

        # Move away from target
        target_pos = movement_system.em.get_component(ai.target_entity, Position)
        if not target_pos:
            return []

        dx = -1 if target_pos.x > position.x else (1 if target_pos.x < position.x else 0)
        dy = -1 if target_pos.y > position.y else (1 if target_pos.y < position.y else 0)

        return [ActionScore(
            action="retreat",
            score=0.7,
            data={"dx": dx, "dy": dy}
        )]

    return {
        "move": score_move,
        "attack": score_attack,
        "skill": score_skill,
        "retreat": score_retreat,
    }
