"""Character definitions and templates."""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class CharacterBaseStats:
    """Base stats for a character."""
    hp: int = 50
    energy: int = 30
    power: int = 5
    defense: int = 0
    crit_chance: float = 0.05
    crit_multiplier: float = 2.0


@dataclass
class CharacterSkillSlot:
    """A skill slot with key binding."""
    key: str  # Q, W, E, R
    skill_id: str
    unlocked_at_level: int = 1


@dataclass
class CharacterMechanic:
    """Unique character mechanic."""
    name: str
    description: str
    resource_name: str = ""  # e.g., "Rage", "Echoes", "Infection"
    resource_max: int = 0
    starting_resource: int = 0


@dataclass
class Character:
    """Complete character definition."""
    id: str
    name: str
    title: str
    description: str
    lore: str = ""
    
    # Visual
    symbol: str = "@"
    color: str = "white"
    
    # Stats
    base_stats: CharacterBaseStats = field(default_factory=CharacterBaseStats)
    
    # Skills
    skills: List[CharacterSkillSlot] = field(default_factory=list)
    
    # Unique mechanic
    mechanic: CharacterMechanic | None = None
    
    # Starting tags
    starting_tags: List[str] = field(default_factory=list)
    
    # Difficulty rating (1-5)
    difficulty: int = 2


# ============================================================================
# CHARACTER 1: THE EXECUTIONER
# ============================================================================

EXECUTIONER = Character(
    id="executioner",
    name="The Executioner",
    title="Blood-Fueled Berserker",
    description="A brutal melee fighter who grows stronger as health decreases.",
    lore="""
        Once the royal headsman, now a vessel of pure rage.
        The Executioner trades life for power, each wound fueling 
        the next devastating strike. Blood is not weakness—it is 
        ammunition.
    """,
    symbol="⚔",
    color="red",
    base_stats=CharacterBaseStats(
        hp=60,
        energy=25,
        power=7,
        defense=1,
        crit_chance=0.10,
        crit_multiplier=2.2,
    ),
    skills=[
        CharacterSkillSlot(key="Q", skill_id="cleave"),
        CharacterSkillSlot(key="W", skill_id="chain_hook"),
        CharacterSkillSlot(key="E", skill_id="blood_surge"),
        CharacterSkillSlot(key="R", skill_id="execution"),
    ],
    mechanic=CharacterMechanic(
        name="Rage",
        description="Lower HP increases damage. At 50% HP or below, gain +50% power.",
        resource_name="Rage",
        resource_max=100,
        starting_resource=0,
    ),
    starting_tags=["PHYSICAL", "BLOOD", "MELEE"],
    difficulty=2,
)

# ============================================================================
# CHARACTER 2: THE ASTROMANCER
# ============================================================================

ASTROMANCER = Character(
    id="astromancer",
    name="The Astromancer",
    title="Temporal Manipulator",
    description="Commands space and time, with abilities that echo across turns.",
    lore="""
        A scholar of the void who pierced the veil between moments.
        The Astromancer does not cast spells once—they cast them
        across time itself. Each ability leaves an echo, waiting
        to collapse into devastating synergy.
    """,
    symbol="✦",
    color="purple",
    base_stats=CharacterBaseStats(
        hp=40,
        energy=40,
        power=6,
        defense=0,
        crit_chance=0.08,
        crit_multiplier=2.5,
    ),
    skills=[
        CharacterSkillSlot(key="Q", skill_id="star_bolt"),
        CharacterSkillSlot(key="W", skill_id="warp_step"),
        CharacterSkillSlot(key="E", skill_id="echo_seal"),
        CharacterSkillSlot(key="R", skill_id="collapse"),
    ],
    mechanic=CharacterMechanic(
        name="Echo",
        description="Skills can be marked to repeat after 2 turns. Collapse triggers all echoes.",
        resource_name="Echoes",
        resource_max=5,
        starting_resource=0,
    ),
    starting_tags=["VOID", "ECHO", "PROJECTILE"],
    difficulty=4,
)

# ============================================================================
# CHARACTER 3: THE PLAGUE SAINT
# ============================================================================

PLAGUE_SAINT = Character(
    id="plague_saint",
    name="The Plague Saint",
    title="Harbinger of Infection",
    description="Corrupts the arena itself, spreading disease that explodes.",
    lore="""
        Blessed by a dying god of decay, the Plague Saint carries
        salvation through infection. To be infected is to be part
        of the whole—and when the time comes, to bloom into
        something beautiful and terrible.
    """,
    symbol="☣",
    color="green",
    base_stats=CharacterBaseStats(
        hp=45,
        energy=35,
        power=5,
        defense=0,
        crit_chance=0.05,
        crit_multiplier=2.0,
    ),
    skills=[
        CharacterSkillSlot(key="Q", skill_id="rot_touch"),
        CharacterSkillSlot(key="W", skill_id="spore_cloud"),
        CharacterSkillSlot(key="E", skill_id="harvest"),
        CharacterSkillSlot(key="R", skill_id="bloom"),
    ],
    mechanic=CharacterMechanic(
        name="Infection",
        description="Poisoned enemies spread infection to nearby foes. Harvest explodes them.",
        resource_name="Infection",
        resource_max=100,
        starting_resource=0,
    ),
    starting_tags=["POISON", "DOT", "AOE"],
    difficulty=3,
)

# ============================================================================
# CHARACTER 4: THE MIRROR DUELIST
# ============================================================================

MIRROR_DUELIST = Character(
    id="mirror_duelist",
    name="The Mirror Duelist",
    title="Master of Reflection",
    description="Precision fighter who counters attacks and predicts enemy moves.",
    lore="""
        Trained in the Hall of Thousand Mirrors, the Duelist sees
        every attack before it happens. Through perfect timing and
        flawless technique, they turn enemy strength against itself.
        The perfect counter kills faster than any strike.
    """,
    symbol="◈",
    color="cyan",
    base_stats=CharacterBaseStats(
        hp=45,
        energy=35,
        power=6,
        defense=0,
        crit_chance=0.12,
        crit_multiplier=2.3,
    ),
    skills=[
        CharacterSkillSlot(key="Q", skill_id="feint"),
        CharacterSkillSlot(key="W", skill_id="mirror_step"),
        CharacterSkillSlot(key="E", skill_id="riposte"),
        CharacterSkillSlot(key="R", skill_id="perfect_reflection"),
    ],
    mechanic=CharacterMechanic(
        name="Focus",
        description="Build Focus through successful dodges and counters. Spend for guaranteed crits.",
        resource_name="Focus",
        resource_max=5,
        starting_resource=0,
    ),
    starting_tags=["PHYSICAL", "CRIT", "COUNTER"],
    difficulty=5,
)

# ============================================================================
# CHARACTER REGISTRY
# ============================================================================

ALL_CHARACTERS: dict[str, Character] = {
    EXECUTIONER.id: EXECUTIONER,
    ASTROMANCER.id: ASTROMANCER,
    PLAGUE_SAINT.id: PLAGUE_SAINT,
    MIRROR_DUELIST.id: MIRROR_DUELIST,
}


def get_character(character_id: str) -> Character | None:
    """Get a character by ID."""
    return ALL_CHARACTERS.get(character_id)


def get_all_characters() -> list[Character]:
    """Get all available characters."""
    return list(ALL_CHARACTERS.values())


def apply_character_template(entity_manager: Any, entity_id: int, character: Character) -> None:
    """Apply character template to an entity, setting up all components."""
    from src.components import (
        Position, Renderable, Health, Energy, Stats,
        Skills, Cooldowns, Statuses, Faction, Tags, Level, Movement
    )
    from src.core.constants import FACTION_PLAYER
    
    # Update renderable
    renderable = entity_manager.get_component(entity_id, Renderable)
    if renderable:
        renderable.symbol = character.symbol
        renderable.color = character.color
        renderable.bold = True
    
    # Update health
    health = entity_manager.get_component(entity_id, Health)
    if health:
        health.maximum = character.base_stats.hp
        health.current = health.maximum
    
    # Update energy
    energy = entity_manager.get_component(entity_id, Energy)
    if energy:
        energy.maximum = character.base_stats.energy
        energy.current = energy.maximum
    
    # Update stats
    stats = entity_manager.get_component(entity_id, Stats)
    if stats:
        stats.power = character.base_stats.power
        stats.defense = character.base_stats.defense
        stats.crit_chance = character.base_stats.crit_chance
        stats.crit_multiplier = character.base_stats.crit_multiplier
    
    # Set skills
    skills = entity_manager.get_component(entity_id, Skills)
    if skills:
        skills.active_skills = [slot.skill_id for slot in character.skills]
    
    # Add starting tags
    tags = entity_manager.get_component(entity_id, Tags)
    if tags:
        for tag in character.starting_tags:
            tags.add(tag)
    
    # Note: Mechanic-specific state would be stored in additional components
    # For MVP, we track mechanics through status effects and custom logic
