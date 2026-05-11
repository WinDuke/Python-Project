"""Core ECS components for TURNBOUND."""

from dataclasses import dataclass, field
from typing import Dict, List, Set

from src.core.constants import FACTION_PLAYER


@dataclass
class Position:
    """Grid position component."""
    x: int = 0
    y: int = 0

    def set(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def offset(self, dx: int, dy: int) -> tuple[int, int]:
        return (self.x + dx, self.y + dy)


@dataclass
class Renderable:
    """ASCII rendering component."""
    symbol: str = "@"
    color: str = "white"
    bg_color: str | None = None
    bold: bool = False
    dim: bool = False
    blink: bool = False
    render_priority: int = 0  # Higher = rendered on top


@dataclass
class Health:
    """Health pool component."""
    current: int = 50
    maximum: int = 50

    @property
    def is_dead(self) -> bool:
        return self.current <= 0

    @property
    def percent(self) -> float:
        if self.maximum <= 0:
            return 0.0
        return self.current / self.maximum

    def damage(self, amount: int) -> int:
        """Apply damage and return actual damage taken."""
        actual = min(amount, self.current)
        self.current -= actual
        return actual

    def heal(self, amount: int) -> int:
        """Heal and return actual healing done."""
        old = self.current
        self.current = min(self.current + amount, self.maximum)
        return self.current - old


@dataclass
class Energy:
    """Skill resource component."""
    current: int = 30
    maximum: int = 30

    @property
    def percent(self) -> float:
        if self.maximum <= 0:
            return 0.0
        return self.current / self.maximum

    def spend(self, amount: int) -> bool:
        """Spend energy, returns True if successful."""
        if self.current >= amount:
            self.current -= amount
            return True
        return False

    def restore(self, amount: int) -> int:
        """Restore energy and return actual amount restored."""
        old = self.current
        self.current = min(self.current + amount, self.maximum)
        return self.current - old


@dataclass
class Stats:
    """Combat statistics component."""
    power: int = 5  # Damage scaling
    defense: int = 0  # Flat mitigation
    crit_chance: float = 0.05
    crit_multiplier: float = 2.0
    speed: int = 1  # Turn order priority
    evasion: float = 0.0  # Dodge chance


@dataclass
class Skills:
    """Known abilities component."""
    active_skills: List[str] = field(default_factory=list)  # Skill IDs
    passive_skills: List[str] = field(default_factory=list)
    triggered_skills: List[str] = field(default_factory=list)

    def has_skill(self, skill_id: str) -> bool:
        return skill_id in self.active_skills or skill_id in self.passive_skills


@dataclass
class Cooldowns:
    """Cooldown tracking component."""
    cooldowns: Dict[str, int] = field(default_factory=dict)  # skill_id -> turns remaining

    def start(self, skill_id: str, duration: int) -> None:
        self.cooldowns[skill_id] = duration

    def tick(self) -> None:
        """Decrement all cooldowns by 1."""
        for skill_id in list(self.cooldowns.keys()):
            self.cooldowns[skill_id] -= 1
            if self.cooldowns[skill_id] <= 0:
                del self.cooldowns[skill_id]

    def is_ready(self, skill_id: str) -> bool:
        return skill_id not in self.cooldowns

    def get_remaining(self, skill_id: str) -> int:
        return self.cooldowns.get(skill_id, 0)


@dataclass
class StatusEffect:
    """A single status effect instance."""
    effect_type: str
    stacks: int = 1
    duration: int = 0  # 0 = permanent until removed
    magnitude: float = 1.0  # Effect strength modifier


@dataclass
class Statuses:
    """Active status effects component."""
    effects: Dict[str, StatusEffect] = field(default_factory=dict)

    def add(self, effect_type: str, duration: int = 0, magnitude: float = 1.0, stack: bool = True) -> None:
        if effect_type in self.effects:
            existing = self.effects[effect_type]
            if stack:
                existing.stacks += 1
            existing.duration = max(existing.duration, duration)
            existing.magnitude = max(existing.magnitude, magnitude)
        else:
            self.effects[effect_type] = StatusEffect(
                effect_type=effect_type,
                duration=duration,
                magnitude=magnitude,
                stacks=1
            )

    def remove(self, effect_type: str) -> None:
        self.effects.pop(effect_type, None)

    def has(self, effect_type: str) -> bool:
        return effect_type in self.effects

    def get(self, effect_type: str) -> StatusEffect | None:
        return self.effects.get(effect_type)

    def tick(self) -> list[str]:
        """Tick down durations and return expired effects."""
        expired = []
        for effect_type in list(self.effects.keys()):
            effect = self.effects[effect_type]
            if effect.duration > 0:
                effect.duration -= 1
                if effect.duration <= 0:
                    expired.append(effect_type)
        for effect_type in expired:
            del self.effects[effect_type]
        return expired


@dataclass
class AI:
    """AI behavior profile component."""
    behavior_type: str = "aggressive"  # aggressive, defensive, tactical, frenzied
    target_entity: int | None = None
    aggression: float = 0.8  # 0-1, higher = more likely to attack
    preferred_range: int = 1  # Desired distance from target
    retreat_threshold: float = 0.3  # HP% at which to consider retreating
    skills: List[str] = field(default_factory=list)  # Available AI skills


@dataclass
class Faction:
    """Faction identification component."""
    faction_id: int = FACTION_PLAYER


@dataclass
class Tags:
    """Gameplay tags for synergies and interactions."""
    tags: Set[str] = field(default_factory=set)

    def add(self, tag: str) -> None:
        self.tags.add(tag)

    def has(self, tag: str) -> bool:
        return tag in self.tags

    def remove(self, tag: str) -> None:
        self.tags.discard(tag)

    def has_any(self, tags: list[str]) -> bool:
        return any(tag in self.tags for tag in tags)

    def has_all(self, tags: list[str]) -> bool:
        return all(tag in self.tags for tag in tags)


@dataclass
class Level:
    """Character level and experience."""
    current: int = 1
    exp: int = 0
    exp_to_next: int = 20

    def add_exp(self, amount: int) -> bool:
        """Add EXP and return True if leveled up."""
        self.exp += amount
        if self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.current += 1
            self.exp_to_next = int(self.exp_to_next * 1.5)
            return True
        return False


@dataclass
class Movement:
    """Movement capabilities."""
    move_cost: int = 1  # AP cost per tile
    can_diagonal: bool = True
    can_pass_through: bool = False  # Ghost movement
    immobilized: bool = False
