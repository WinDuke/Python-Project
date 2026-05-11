"""Combat system for TURNBOUND."""

import random
from typing import TYPE_CHECKING

from src.core.constants import (
    BASE_CRIT_CHANCE,
    BASE_CRIT_MULTIPLIER,
    DAMAGE_FIRE,
    DAMAGE_PHYSICAL,
    STATUS_BURN,
    STATUS_SHOCK,
    STATUS_VULNERABLE,
)
from src.core.event_bus import GameEvent, EventBus

if TYPE_CHECKING:
    from src.ecs.entity_manager import EntityManager


class CombatSystem:
    """Handles all combat calculations and damage resolution."""

    def __init__(self, entity_manager: "EntityManager", event_bus: EventBus):
        self.em = entity_manager
        self.event_bus = event_bus

    def calculate_damage(
        self,
        attacker_id: int,
        target_id: int,
        base_damage: int,
        damage_type: str = DAMAGE_PHYSICAL,
    ) -> tuple[int, bool]:
        """
        Calculate final damage after all modifiers.
        Returns (damage_amount, is_crit).
        """
        from src.components import Health, Stats, Statuses

        # Get attacker stats
        attacker_stats = self.em.get_component(attacker_id, Stats)
        if not attacker_stats:
            attacker_stats = Stats()

        # Get target stats
        target_stats = self.em.get_component(target_id, Stats)
        if not target_stats:
            target_stats = Stats()

        target_statuses = self.em.get_component(target_id, Statuses)

        # Base formula: (BaseDamage + Power) × CritMultiplier - Defense
        power = attacker_stats.power
        defense = target_stats.defense

        # Check for critical hit
        crit_chance = attacker_stats.crit_chance
        is_crit = random.random() < crit_chance
        crit_multiplier = attacker_stats.crit_multiplier if is_crit else 1.0

        # Apply vulnerability status
        if target_statuses and target_statuses.has(STATUS_VULNERABLE):
            vuln_effect = target_statuses.get(STATUS_VULNERABLE)
            if vuln_effect:
                crit_multiplier *= (1.0 + (0.5 * vuln_effect.stacks))

        # Calculate pre-mitigation damage
        pre_mitigation = (base_damage + power) * crit_multiplier

        # Apply defense (flat reduction)
        final_damage = max(1, int(pre_mitigation - defense))

        # Apply damage type modifiers
        final_damage = self._apply_type_modifiers(final_damage, damage_type, target_statuses)

        return (final_damage, is_crit)

    def _apply_type_modifiers(
        self, damage: int, damage_type: str, statuses: "Statuses | None"
    ) -> int:
        """Apply damage type specific modifiers."""
        if not statuses:
            return damage

        # Shock increases damage taken
        if statuses.has(STATUS_SHOCK):
            shock_effect = statuses.get(STATUS_SHOCK)
            if shock_effect:
                damage = int(damage * (1.0 + (0.25 * shock_effect.stacks)))

        return damage

    def deal_damage(
        self,
        attacker_id: int,
        target_id: int,
        base_damage: int,
        damage_type: str = DAMAGE_PHYSICAL,
    ) -> int:
        """Deal damage to a target and emit events."""
        from src.components import Health

        # Calculate damage
        final_damage, is_crit = self.calculate_damage(
            attacker_id, target_id, base_damage, damage_type
        )

        # Apply damage
        target_health = self.em.get_component(target_id, Health)
        if target_health:
            actual_damage = target_health.damage(final_damage)

            # Emit events
            if is_crit:
                self.event_bus.emit(
                    GameEvent(
                        event_type="crit",
                        source=attacker_id,
                        target=target_id,
                        data={"damage": actual_damage, "damage_type": damage_type},
                    )
                )
            else:
                self.event_bus.emit(
                    GameEvent(
                        event_type="hit",
                        source=attacker_id,
                        target=target_id,
                        data={"damage": actual_damage, "damage_type": damage_type},
                    )
                )

            self.event_bus.emit(
                GameEvent(
                    event_type="damage_dealt",
                    source=attacker_id,
                    target=target_id,
                    data={"damage": actual_damage, "damage_type": damage_type},
                )
            )

            self.event_bus.emit(
                GameEvent(
                    event_type="damage_taken",
                    source=attacker_id,
                    target=target_id,
                    data={"damage": actual_damage, "damage_type": damage_type},
                )
            )

            # Check for death
            if target_health.is_dead:
                self.event_bus.emit(
                    GameEvent(
                        event_type="kill",
                        source=attacker_id,
                        target=target_id,
                        data={},
                    )
                )

            return actual_damage

        return 0

    def apply_status(
        self,
        source_id: int,
        target_id: int,
        effect_type: str,
        duration: int = 0,
        magnitude: float = 1.0,
    ) -> bool:
        """Apply a status effect to a target."""
        from src.components import Statuses

        target_statuses = self.em.get_component(target_id, Statuses)
        if not target_statuses:
            return False

        target_statuses.add(effect_type, duration, magnitude)

        self.event_bus.emit(
            GameEvent(
                event_type="status_apply",
                source=source_id,
                target=target_id,
                data={"effect_type": effect_type, "duration": duration},
            )
        )

        return True

    def remove_status(self, target_id: int, effect_type: str) -> bool:
        """Remove a status effect from a target."""
        from src.components import Statuses

        target_statuses = self.em.get_component(target_id, Statuses)
        if not target_statuses or not target_statuses.has(effect_type):
            return False

        target_statuses.remove(effect_type)

        self.event_bus.emit(
            GameEvent(
                event_type="status_remove",
                target=target_id,
                data={"effect_type": effect_type},
            )
        )

        return True

    def tick_statuses(self, entity_id: int) -> list[str]:
        """Tick down status durations and return expired effects."""
        from src.components import Statuses

        statuses = self.em.get_component(entity_id, Statuses)
        if not statuses:
            return []

        expired = statuses.tick()
        for effect_type in expired:
            self.event_bus.emit(
                GameEvent(
                    event_type="status_remove",
                    target=entity_id,
                    data={"effect_type": effect_type, "reason": "expired"},
                )
            )

        return expired

    def heal(self, healer_id: int, target_id: int, amount: int) -> int:
        """Heal a target and emit events."""
        from src.components import Health

        target_health = self.em.get_component(target_id, Health)
        if not target_health:
            return 0

        actual_heal = target_health.heal(amount)

        self.event_bus.emit(
            GameEvent(
                event_type="heal",
                source=healer_id,
                target=target_id,
                data={"amount": actual_heal},
            )
        )

        return actual_heal
