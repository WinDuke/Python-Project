"""Enemy definitions and templates."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EnemyStats:
    """Enemy combat stats."""
    hp: int = 20
    power: int = 3
    defense: int = 0
    crit_chance: float = 0.05
    crit_multiplier: float = 1.8
    speed: int = 1
    evasion: float = 0.0


@dataclass
class EnemyBehavior:
    """AI behavior configuration."""
    type: str = "aggressive"  # aggressive, defensive, tactical, frenzied, coward
    preferred_range: int = 1
    aggression: float = 0.8
    retreat_threshold: float = 0.3


@dataclass
class Enemy:
    """Complete enemy definition."""
    id: str
    name: str
    description: str = ""
    
    # Visual
    symbol: str = "e"
    color: str = "red"
    bold: bool = False
    
    # Combat
    stats: EnemyStats = field(default_factory=EnemyStats)
    behavior: EnemyBehavior = field(default_factory=EnemyBehavior)
    
    # Threat cost (for wave budget)
    threat_cost: int = 2
    
    # Skills
    skills: List[str] = field(default_factory=list)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # EXP reward
    exp_reward: int = 10
    
    # Elite modifier (optional)
    elite_modifier: Optional[str] = None


# ============================================================================
# BASIC ENEMIES
# ============================================================================

ZOMBIE = Enemy(
    id="zombie",
    name="Zombie",
    description="Shambling corpse that attacks anything living.",
    symbol="z",
    color="green",
    stats=EnemyStats(
        hp=15,
        power=2,
        defense=0,
    ),
    behavior=EnemyBehavior(
        type="aggressive",
        preferred_range=1,
        aggression=0.9,
    ),
    threat_cost=2,
    skills=["zombie_slam"],
    tags=["UNDEAD", "MELEE"],
    exp_reward=5,
)

SKELETON = Enemy(
    id="skeleton",
    name="Skeleton",
    description="Animated bones with a rusty blade.",
    symbol="s",
    color="white",
    stats=EnemyStats(
        hp=12,
        power=3,
        defense=0,
        crit_chance=0.10,
    ),
    behavior=EnemyBehavior(
        type="aggressive",
        preferred_range=1,
        aggression=0.85,
    ),
    threat_cost=2,
    skills=["zombie_slam"],
    tags=["UNDEAD", "MELEE"],
    exp_reward=5,
)

SPITTER = Enemy(
    id="spitter",
    name="Spitter",
    description="Bloated creature that spews corrosive acid.",
    symbol="🦠",
    color="lime",
    stats=EnemyStats(
        hp=10,
        power=2,
        defense=0,
    ),
    behavior=EnemyBehavior(
        type="defensive",
        preferred_range=4,
        aggression=0.5,
        retreat_threshold=0.4,
    ),
    threat_cost=4,
    skills=["spit_acid"],
    tags=["BEAST", "RANGED", "POISON"],
    exp_reward=8,
)

GNOLL = Enemy(
    id="gnoll",
    name="Gnoll",
    description="Savage hyena-kin that hunts in packs.",
    symbol="g",
    color="yellow",
    bold=True,
    stats=EnemyStats(
        hp=18,
        power=4,
        defense=0,
        speed=2,
    ),
    behavior=EnemyBehavior(
        type="frenzied",
        preferred_range=1,
        aggression=1.0,
    ),
    threat_cost=3,
    skills=["zombie_slam"],
    tags=["BEAST", "MELEE", "PACK"],
    exp_reward=7,
)

# ============================================================================
# TANK ENEMIES
# ============================================================================

KNIGHT = Enemy(
    id="knight",
    name="Cursed Knight",
    description="Armored warrior bound to eternal service.",
    symbol="♘",
    color="grey50",
    bold=True,
    stats=EnemyStats(
        hp=35,
        power=4,
        defense=3,
        crit_chance=0.05,
    ),
    behavior=EnemyBehavior(
        type="defensive",
        preferred_range=1,
        aggression=0.6,
    ),
    threat_cost=6,
    skills=["knight_strike"],
    tags=["HUMANOID", "MELEE", "ARMORED"],
    exp_reward=12,
)

GOLEM = Enemy(
    id="golem",
    name="Stone Golem",
    description="Animated construct of stone and magic.",
    symbol="▓",
    color="grey42",
    bold=True,
    stats=EnemyStats(
        hp=50,
        power=5,
        defense=5,
        speed=0,
    ),
    behavior=EnemyBehavior(
        type="defensive",
        preferred_range=1,
        aggression=0.4,
    ),
    threat_cost=8,
    skills=["zombie_slam"],
    tags=["CONSTRUCT", "MELEE", "ARMORED"],
    exp_reward=15,
)

# ============================================================================
# CASTER ENEMIES
# ============================================================================

NECROMANCER = Enemy(
    id="necromancer",
    name="Necromancer",
    description="Dark mage who raises the dead.",
    symbol="☤",
    color="purple",
    bold=True,
    stats=EnemyStats(
        hp=20,
        power=6,
        defense=0,
        crit_chance=0.15,
    ),
    behavior=EnemyBehavior(
        type="tactical",
        preferred_range=5,
        aggression=0.5,
        retreat_threshold=0.4,
    ),
    threat_cost=10,
    skills=["summon_minion", "curse_weakness"],
    tags=["HUMANOID", "RANGED", "SUMMONER", "VOID"],
    exp_reward=18,
)

PYROMANCER = Enemy(
    id="pyromancer",
    name="Pyromancer",
    description="Fire-wielding cultist.",
    symbol="🔥",
    color="red",
    bold=True,
    stats=EnemyStats(
        hp=18,
        power=7,
        defense=0,
        crit_chance=0.20,
    ),
    behavior=EnemyBehavior(
        type="aggressive",
        preferred_range=4,
        aggression=0.7,
    ),
    threat_cost=8,
    skills=["spit_acid"],  # Reusing as fireball for MVP
    tags=["HUMANOID", "RANGED", "FIRE"],
    exp_reward=15,
)

SHAMAN = Enemy(
    id="shaman",
    name="Blood Shaman",
    description="Tribal healer who buffs allies.",
    symbol="⚕",
    color="orange",
    bold=True,
    stats=EnemyStats(
        hp=22,
        power=4,
        defense=0,
    ),
    behavior=EnemyBehavior(
        type="tactical",
        preferred_range=4,
        aggression=0.4,
        retreat_threshold=0.5,
    ),
    threat_cost=7,
    skills=["curse_weakness"],
    tags=["HUMANOID", "RANGED", "SUPPORT", "BLOOD"],
    exp_reward=14,
)

# ============================================================================
# SPECIAL ENEMIES
# ============================================================================

WRAITH = Enemy(
    id="wraith",
    name="Wraith",
    description="Ethereal undead that phases through matter.",
    symbol="W",
    color="cyan",
    bold=True,
    stats=EnemyStats(
        hp=16,
        power=5,
        defense=0,
        evasion=0.3,
    ),
    behavior=EnemyBehavior(
        type="tactical",
        preferred_range=1,
        aggression=0.8,
    ),
    threat_cost=6,
    skills=["zombie_slam"],
    tags=["UNDEAD", "MELEE", "ETHEREAL"],
    exp_reward=12,
)

BERSERKER = Enemy(
    id="berserker",
    name="Blood Berserker",
    description="Mad warrior who grows stronger when wounded.",
    symbol="💢",
    color="red",
    bold=True,
    stats=EnemyStats(
        hp=25,
        power=6,
        defense=0,
        crit_chance=0.20,
        crit_multiplier=2.5,
    ),
    behavior=EnemyBehavior(
        type="frenzied",
        preferred_range=1,
        aggression=1.0,
        retreat_threshold=0.1,
    ),
    threat_cost=7,
    skills=["zombie_slam"],
    tags=["HUMANOID", "MELEE", "BLOOD"],
    exp_reward=14,
)

ASSASSIN = Enemy(
    id="assassin",
    name="Shadow Assassin",
    description="Silent killer who strikes from darkness.",
    symbol="🗡",
    color="magenta",
    bold=True,
    stats=EnemyStats(
        hp=14,
        power=8,
        defense=0,
        crit_chance=0.30,
        crit_multiplier=3.0,
        speed=2,
    ),
    behavior=EnemyBehavior(
        type="tactical",
        preferred_range=1,
        aggression=0.9,
    ),
    threat_cost=8,
    skills=["zombie_slam"],
    tags=["HUMANOID", "MELEE", "CRIT"],
    exp_reward=16,
)

# ============================================================================
# ELITE ENEMIES
# ============================================================================

ELITE_ZOMBIE = Enemy(
    id="elite_zombie",
    name="Grotesque Horror",
    description="A massive zombie bloated with corruption.",
    symbol="Z",
    color="dark_green",
    bold=True,
    stats=EnemyStats(
        hp=40,
        power=5,
        defense=2,
    ),
    behavior=EnemyBehavior(
        type="aggressive",
        preferred_range=1,
        aggression=0.8,
    ),
    threat_cost=15,
    skills=["zombie_slam"],
    tags=["UNDEAD", "MELEE", "ELITE"],
    exp_reward=25,
    elite_modifier="tanky",
)

ELITE_SKELETON = Enemy(
    id="elite_skeleton",
    name="Bone Lord",
    description="Ancient skeleton general commanding the undead.",
    symbol="S",
    color="gold",
    bold=True,
    stats=EnemyStats(
        hp=30,
        power=7,
        defense=1,
        crit_chance=0.25,
    ),
    behavior=EnemyBehavior(
        type="tactical",
        preferred_range=1,
        aggression=0.7,
    ),
    threat_cost=15,
    skills=["knight_strike"],
    tags=["UNDEAD", "MELEE", "ELITE", "COMMANDER"],
    exp_reward=25,
    elite_modifier="damage",
)

ELITE_PYROMANCER = Enemy(
    id="elite_pyromancer",
    name="Flame Archon",
    description="Master of flames who leaves burning ground.",
    symbol="🔥",
    color="bright_red",
    bold=True,
    stats=EnemyStats(
        hp=28,
        power=9,
        defense=0,
        crit_chance=0.25,
    ),
    behavior=EnemyBehavior(
        type="aggressive",
        preferred_range=5,
        aggression=0.8,
    ),
    threat_cost=15,
    skills=["spit_acid"],
    tags=["HUMANOID", "RANGED", "FIRE", "ELITE"],
    exp_reward=25,
    elite_modifier="fire_aura",
)

ELITE_NECROMANCER = Enemy(
    id="elite_necromancer",
    name="Death Cult Leader",
    description="High priest of the undead legions.",
    symbol="☠",
    color="bright_magenta",
    bold=True,
    stats=EnemyStats(
        hp=32,
        power=8,
        defense=1,
    ),
    behavior=EnemyBehavior(
        type="tactical",
        preferred_range=6,
        aggression=0.6,
    ),
    threat_cost=15,
    skills=["summon_minion", "curse_weakness"],
    tags=["HUMANOID", "RANGED", "SUMMONER", "VOID", "ELITE"],
    exp_reward=25,
    elite_modifier="summoner",
)

# ============================================================================
# ENEMY REGISTRY
# ============================================================================

ALL_ENEMIES: dict[str, Enemy] = {
    # Basic
    ZOMBIE.id: ZOMBIE,
    SKELETON.id: SKELETON,
    SPITTER.id: SPITTER,
    GNOLL.id: GNOLL,
    # Tank
    KNIGHT.id: KNIGHT,
    GOLEM.id: GOLEM,
    # Caster
    NECROMANCER.id: NECROMANCER,
    PYROMANCER.id: PYROMANCER,
    SHAMAN.id: SHAMAN,
    # Special
    WRAITH.id: WRAITH,
    BERSERKER.id: BERSERKER,
    ASSASSIN.id: ASSASSIN,
    # Elite
    ELITE_ZOMBIE.id: ELITE_ZOMBIE,
    ELITE_SKELETON.id: ELITE_SKELETON,
    ELITE_PYROMANCER.id: ELITE_PYROMANCER,
    ELITE_NECROMANCER.id: ELITE_NECROMANCER,
}


def get_enemy(enemy_id: str) -> Enemy | None:
    """Get an enemy by ID."""
    return ALL_ENEMIES.get(enemy_id)


def get_enemies_by_tag(tag: str) -> list[Enemy]:
    """Get all enemies with a specific tag."""
    return [e for e in ALL_ENEMIES.values() if tag in e.tags]


def get_basic_enemies() -> list[Enemy]:
    """Get basic (non-elite) enemies."""
    return [e for e in ALL_ENEMIES.values() if not e.elite_modifier]


def get_elite_enemies() -> list[Enemy]:
    """Get elite enemies."""
    return [e for e in ALL_ENEMIES.values() if e.elite_modifier]
