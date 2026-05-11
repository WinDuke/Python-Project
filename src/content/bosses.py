"""Boss definitions and encounter templates."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class BossPhase:
    """A single phase of a boss fight."""
    name: str
    description: str = ""
    
    # Visual changes
    symbol: str = "B"
    color: str = "red"
    
    # Stat modifiers (multipliers)
    hp_modifier: float = 1.0
    power_modifier: float = 1.0
    defense_modifier: float = 1.0
    
    # Skills available in this phase
    skills: List[str] = field(default_factory=list)
    
    # Behavior changes
    aggression: float = 0.8
    preferred_range: int = 1
    
    # Trigger conditions
    trigger_at_hp_percent: float = 1.0  # Phase starts at this HP%
    trigger_at_turn: int = 0  # Or at this turn number
    
    # Arena effects during phase
    arena_effect: Optional[str] = None


@dataclass
class BossMechanic:
    """Special boss mechanic."""
    name: str
    description: str
    trigger_condition: str  # "turn", "hp_threshold", "player_action"
    trigger_value: Any
    effect: str


@dataclass
class Boss:
    """Complete boss definition."""
    id: str
    name: str
    title: str
    description: str
    lore: str = ""
    
    # Visual
    symbol: str = "B"
    color: str = "bright_red"
    bold: bool = True
    
    # Base stats
    base_hp: int = 100
    base_power: int = 8
    base_defense: int = 2
    base_crit_chance: float = 0.10
    base_crit_multiplier: float = 2.0
    
    # Phases
    phases: List[BossPhase] = field(default_factory=list)
    
    # Special mechanics
    mechanics: List[BossMechanic] = field(default_factory=list)
    
    # Skills (all available)
    all_skills: List[str] = field(default_factory=list)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # EXP reward
    exp_reward: int = 100
    
    # Wave number where this boss appears
    first_appearance_wave: int = 5


# ============================================================================
# BOSS 1: THE HOLLOW KING
# ============================================================================

HOLLOW_KING = Boss(
    id="hollow_king",
    name="The Hollow King",
    title="Ruler of the Void",
    description="A fallen monarch whose soul was consumed by darkness.",
    lore="""
        Once he ruled a kingdom of light. Now he commands only shadows.
        The Hollow King fights with the skill of a thousand battles,
        but each strike carries the weight of his emptiness.
        
        He does not fight to win. He fights to feel something.
    """,
    symbol="♔",
    color="bright_magenta",
    base_hp=150,
    base_power=10,
    base_defense=3,
    base_crit_chance=0.15,
    base_crit_multiplier=2.5,
    phases=[
        BossPhase(
            name="Duelist",
            description="Aggressive melee combat with precise strikes.",
            symbol="♔",
            color="magenta",
            hp_modifier=1.0,
            power_modifier=1.0,
            skills=["hollow_strike"],
            aggression=0.9,
            preferred_range=1,
            trigger_at_hp_percent=1.0,
        ),
        BossPhase(
            name="Mirror King",
            description="Creates shadow clones to fight alongside him.",
            symbol="👥",
            color="bright_magenta",
            hp_modifier=0.7,
            power_modifier=1.2,
            skills=["hollow_strike", "mirror_clone"],
            aggression=0.8,
            preferred_range=1,
            trigger_at_hp_percent=0.66,
        ),
        BossPhase(
            name="Void Avatar",
            description="Envelops the arena in darkness.",
            symbol="◈",
            color="white",
            hp_modifier=0.5,
            power_modifier=1.5,
            skills=["hollow_strike", "mirror_clone", "darkness_field"],
            aggression=1.0,
            preferred_range=1,
            trigger_at_hp_percent=0.33,
            arena_effect="darkness",
        ),
    ],
    mechanics=[
        BossMechanic(
            name="Royal Decree",
            description="Every 5 turns, summons a mirror clone.",
            trigger_condition="turn",
            trigger_value=5,
            effect="summon_clone",
        ),
        BossMechanic(
            name="Empty Crown",
            description="When a clone dies, the King gains power.",
            trigger_condition="clone_death",
            trigger_value=None,
            effect="power_boost",
        ),
    ],
    all_skills=["hollow_strike", "mirror_clone", "darkness_field"],
    tags=["VOID", "MELEE", "SUMMONER", "PHASES"],
    exp_reward=150,
    first_appearance_wave=5,
)

# ============================================================================
# BOSS 2: THE BELL SAINT
# ============================================================================

BELL_SAINT = Boss(
    id="bell_saint",
    name="The Bell Saint",
    title="Keeper of the Sacred Chime",
    description="A holy warrior who channels divine power through sacred bells.",
    lore="""
        The Bell Saint does not speak. She rings.
        Each chime carries a different blessing—or curse.
        The faithful kneel. The faithless shatter.
        
        Her bell tower has no stairs. Only echoes.
    """,
    symbol="🔔",
    color="gold",
    base_hp=120,
    base_power=8,
    base_defense=4,
    base_crit_chance=0.10,
    base_crit_multiplier=2.0,
    phases=[
        BossPhase(
            name="First Chime",
            description="Standard combat with occasional bell rings.",
            symbol="🔔",
            color="gold",
            hp_modifier=1.0,
            power_modifier=1.0,
            skills=["bell_chime"],
            aggression=0.6,
            preferred_range=3,
            trigger_at_hp_percent=1.0,
        ),
        BossPhase(
            name="Second Chime",
            description="Bell rings more frequently, adding curse fields.",
            symbol="🔔",
            color="bright_yellow",
            hp_modifier=0.8,
            power_modifier=1.2,
            skills=["bell_chime", "curse_field"],
            aggression=0.7,
            preferred_range=3,
            trigger_at_hp_percent=0.5,
        ),
    ],
    mechanics=[
        BossMechanic(
            name="Sacred Chime",
            description="Every 3 turns, ring the bell stunning all enemies.",
            trigger_condition="turn",
            trigger_value=3,
            effect="aoe_stun",
        ),
        BossMechanic(
            name="Curse Resonance",
            description="Curse fields expand every turn.",
            trigger_condition="turn",
            trigger_value=1,
            effect="expand_curse",
        ),
        BossMechanic(
            name="Silence Zone",
            description="At 50% HP, creates zones where skills cannot be used.",
            trigger_condition="hp_threshold",
            trigger_value=0.5,
            effect="create_silence",
        ),
    ],
    all_skills=["bell_chime", "curse_field"],
    tags=["LIGHTNING", "STUN", "ZONE", "PHASES"],
    exp_reward=150,
    first_appearance_wave=10,
)

# ============================================================================
# BOSS 3: CHOIR OF TEETH
# ============================================================================

CHOIR_OF_TEETH = Boss(
    id="choir_of_teeth",
    name="Choir of Teeth",
    title="The Living Cathedral",
    description="The arena itself is alive—a cathedral of bone and sinew.",
    lore="""
        It does not have a body. It IS the body.
        Walls breathe. Floors pulse. Pillars gnash.
        
        The Choir sings in voices that were once human.
        Their hymn has only one verse: consumption.
        
        You are not fighting an enemy. You are inside one.
    """,
    symbol="☠",
    color="bright_red",
    base_hp=200,
    base_power=6,
    base_defense=5,
    base_crit_chance=0.05,
    base_crit_multiplier=1.8,
    phases=[
        BossPhase(
            name="Awakening",
            description="Arena begins to shift slowly.",
            symbol="▓",
            color="red",
            hp_modifier=1.0,
            power_modifier=0.8,
            skills=["wall_shift"],
            aggression=0.5,
            preferred_range=1,
            trigger_at_hp_percent=1.0,
            arena_effect="shifting_walls",
        ),
        BossPhase(
            name="Feeding Frenzy",
            description="Walls move aggressively, crushing everything.",
            symbol="▓",
            color="bright_red",
            hp_modifier=0.7,
            power_modifier=1.3,
            skills=["wall_shift"],
            aggression=0.8,
            preferred_range=1,
            trigger_at_hp_percent=0.5,
            arena_effect="crushing_walls",
        ),
    ],
    mechanics=[
        BossMechanic(
            name="Moving Walls",
            description="Every 2 turns, walls shift in a pattern.",
            trigger_condition="turn",
            trigger_value=2,
            effect="shift_terrain",
        ),
        BossMechanic(
            name="Safe Zones",
            description="Certain tiles are safe from wall movement.",
            trigger_condition="turn",
            trigger_value=1,
            effect="mark_safe_zones",
        ),
        BossMechanic(
            name="Digestive Acid",
            description="Floor tiles become damaging over time.",
            trigger_condition="turn",
            trigger_value=4,
            effect="corrode_floor",
        ),
    ],
    all_skills=["wall_shift"],
    tags=["TERRAIN", "AOE", "ENVIRONMENT", "PHASES"],
    exp_reward=200,
    first_appearance_wave=15,
)

# ============================================================================
# BOSS REGISTRY
# ============================================================================

ALL_BOSSES: dict[str, Boss] = {
    HOLLOW_KING.id: HOLLOW_KING,
    BELL_SAINT.id: BELL_SAINT,
    CHOIR_OF_TEETH.id: CHOIR_OF_TEETH,
}


def get_boss(boss_id: str) -> Boss | None:
    """Get a boss by ID."""
    return ALL_BOSSES.get(boss_id)


def get_boss_for_wave(wave_number: int) -> Boss | None:
    """Get the boss that should appear at a given wave."""
    for boss in ALL_BOSSES.values():
        if wave_number == boss.first_appearance_wave:
            return boss
    return None


def get_boss_waves() -> list[int]:
    """Get all wave numbers where bosses appear."""
    return sorted(b.first_appearance_wave for b in ALL_BOSSES.values())
