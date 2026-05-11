"""Upgrade system for managing player progression."""

from typing import TYPE_CHECKING, Set, List
from src.content.upgrades import Upgrade, generate_upgrade_choices

if TYPE_CHECKING:
    from src.core.game import Game


class UpgradeSystem:
    """Manages player upgrades and build synergies."""
    
    def __init__(self, game: "Game"):
        self.game = game
        self.owned_upgrades: Set[str] = set()
        self.player_tags: Set[str] = set()
        self.stat_modifiers: dict[str, float] = {
            "power": 1.0,
            "defense": 1.0,
            "max_hp": 1.0,
            "max_energy": 1.0,
            "crit_chance": 0.0,  # Additive
            "crit_multiplier": 1.0,
            "physical_damage": 1.0,
            "fire_damage": 1.0,
            "frost_damage": 1.0,
            "lightning_damage": 1.0,
            "void_damage": 1.0,
            "poison_damage": 1.0,
            "blood_damage": 1.0,
        }
        self.triggers: dict[str, List[Upgrade]] = {
            "on_hit": [],
            "on_crit": [],
            "on_kill": [],
            "on_damage_taken": [],
            "on_dash": [],
            "on_teleport": [],
            "on_poisoned_enemy_death": [],
            "on_poison_death": [],
            "on_move_away": [],
        }
        self.mechanic_changes: dict[str, List[Upgrade]] = {}
        self.conditional_bonuses: dict[str, List[Upgrade]] = {}
    
    def add_upgrade(self, upgrade: Upgrade) -> None:
        """Add an upgrade to the player."""
        self.owned_upgrades.add(upgrade.id)
        
        # Add tags
        for tag in upgrade.tags:
            self.player_tags.add(tag)
        
        # Apply effects
        for effect in upgrade.effects:
            self._apply_effect(effect, upgrade)
    
    def _apply_effect(self, effect: "UpgradeEffect", upgrade: Upgrade) -> None:
        """Apply a single upgrade effect."""
        effect_type = effect.type
        
        if effect_type == "stat_mod":
            # Apply stat modifier
            if effect.target in self.stat_modifiers:
                if effect.target in ["crit_chance"]:
                    # Additive for crit chance
                    self.stat_modifiers[effect.target] += effect.magnitude
                else:
                    # Multiplicative for others
                    self.stat_modifiers[effect.target] *= effect.magnitude
        
        elif effect_type == "trigger":
            # Register trigger
            if effect.target in self.triggers:
                self.triggers[effect.target].append(upgrade)
        
        elif effect_type == "mechanic_change":
            # Register mechanic change
            if effect.target not in self.mechanic_changes:
                self.mechanic_changes[effect.target] = []
            self.mechanic_changes[effect.target].append(upgrade)
        
        elif effect_type == "conditional_stat":
            # Register conditional bonus
            if effect.condition not in self.conditional_bonuses:
                self.conditional_bonuses[effect.condition] = []
            self.conditional_bonuses[effect.condition].append(upgrade)
    
    def get_stat(self, stat_name: str, base_value: float) -> float:
        """Get modified stat value."""
        modifier = self.stat_modifiers.get(stat_name, 1.0)
        
        if stat_name == "crit_chance":
            return base_value + modifier
        else:
            return base_value * modifier
    
    def get_damage_modifier(self, damage_type: str) -> float:
        """Get damage modifier for a damage type."""
        type_map = {
            "physical": "physical_damage",
            "fire": "fire_damage",
            "frost": "frost_damage",
            "lightning": "lightning_damage",
            "void": "void_damage",
            "poison": "poison_damage",
            "blood": "blood_damage",
        }
        
        stat_key = type_map.get(damage_type, "physical_damage")
        return self.stat_modifiers.get(stat_key, 1.0)
    
    def trigger_event(self, event_type: str, context: dict = None) -> None:
        """Trigger an event for all registered upgrades."""
        context = context or {}
        
        if event_type not in self.triggers:
            return
        
        for upgrade in self.triggers[event_type]:
            self._execute_trigger(upgrade, context)
    
    def _execute_trigger(self, upgrade: Upgrade, context: dict) -> None:
        """Execute a trigger effect."""
        # This would integrate with combat system
        # For MVP, we log the trigger
        pass
    
    def check_conditional(self, condition: str) -> dict[str, float]:
        """Check conditional bonuses and return stat modifications."""
        if condition not in self.conditional_bonuses:
            return {}
        
        modifiers = {}
        for upgrade in self.conditional_bonuses[condition]:
            for effect in upgrade.effects:
                if effect.type == "conditional_stat" and effect.condition == condition:
                    if effect.target not in modifiers:
                        modifiers[effect.target] = 1.0
                    modifiers[effect.target] *= effect.magnitude
        
        return modifiers
    
    def has_mechanic(self, mechanic_name: str) -> bool:
        """Check if a mechanic change is active."""
        return mechanic_name in self.mechanic_changes
    
    def generate_choices(self, num_choices: int = 3) -> List[Upgrade]:
        """Generate upgrade choices for level up."""
        current_wave = self.game.wave_director.state.current_wave if self.game.wave_director else 1
        
        return generate_upgrade_choices(
            player_tags=self.player_tags,
            owned_upgrades=self.owned_upgrades,
            num_choices=num_choices,
            current_wave=current_wave,
        )
    
    def get_build_summary(self) -> dict:
        """Get a summary of the current build."""
        return {
            "upgrades": list(self.owned_upgrades),
            "tags": list(self.player_tags),
            "stat_modifiers": self.stat_modifiers.copy(),
            "active_triggers": {k: len(v) for k, v in self.triggers.items() if v},
            "mechanic_changes": list(self.mechanic_changes.keys()),
        }
    
    def reset(self) -> None:
        """Reset all upgrade state."""
        self.owned_upgrades.clear()
        self.player_tags.clear()
        self.stat_modifiers = {k: 1.0 if k != "crit_chance" else 0.0 for k in self.stat_modifiers}
        for key in self.triggers:
            self.triggers[key] = []
        self.mechanic_changes.clear()
        self.conditional_bonuses.clear()
