"""Skill definitions and data structures."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SkillTarget:
    """Skill targeting configuration."""
    type: str = "self"  # self, single, aoe, line, cone
    range: int = 0
    radius: int = 0
    width: int = 0  # For line/cone
    requires_line_of_sight: bool = True


@dataclass
class SkillEffect:
    """A single effect within a skill."""
    effect_type: str  # damage, heal, status, knockback, etc.
    magnitude: float = 1.0
    duration: int = 0
    damage_type: Optional[str] = None
    status_effect: Optional[str] = None
    scaling: str = "power"  # power, max_hp, current_hp, etc.
    radius: int = 0  # For AOE effects
    stacks: bool = False  # Whether effect can stack
    summon_type: Optional[str] = None  # For summon effects
    zone_type: Optional[str] = None  # For zone creation


@dataclass
class Skill:
    """Complete skill definition."""
    id: str
    name: str
    description: str = ""
    icon: str = "?"
    
    # Targeting
    target: SkillTarget = field(default_factory=SkillTarget)
    
    # Cost and cooldown
    energy_cost: int = 0
    health_cost: int = 0
    cooldown: int = 3
    
    # Effects
    effects: List[SkillEffect] = field(default_factory=list)
    
    # Tags for synergies
    tags: List[str] = field(default_factory=list)
    
    # Animation
    projectile_symbol: str = "*"
    impact_symbol: str = "!"
    animation_duration: int = 150
    
    # AI usage preferences
    ai_priority: float = 1.0
    ai_min_range: int = 0
    ai_max_range: int = 999


# ============================================================================
# CHARACTER SKILLS - THE EXECUTIONER
# ============================================================================

EXECUTIONER_SKILLS = [
    Skill(
        id="cleave",
        name="Cleave",
        description="Strike all enemies in a wide arc in front of you.",
        icon="⚔",
        target=SkillTarget(type="cone", range=3, width=2),
        energy_cost=10,
        cooldown=2,
        effects=[
            SkillEffect(effect_type="damage", magnitude=1.2, damage_type="physical"),
        ],
        tags=["PHYSICAL", "MELEE", "AOE"],
        projectile_symbol="/",
        ai_priority=1.2,
    ),
    Skill(
        id="chain_hook",
        name="Chain Hook",
        description="Pull an enemy to you and deal damage.",
        icon="🪝",
        target=SkillTarget(type="single", range=6),
        energy_cost=15,
        cooldown=4,
        effects=[
            SkillEffect(effect_type="damage", magnitude=0.8, damage_type="physical"),
            SkillEffect(effect_type="knockback", magnitude=-1),  # Negative = pull
        ],
        tags=["PHYSICAL", "PULL", "RANGED"],
        projectile_symbol="↗",
        ai_priority=0.8,
    ),
    Skill(
        id="blood_surge",
        name="Blood Surge",
        description="Spend HP to deal massive damage in an area.",
        icon="💉",
        target=SkillTarget(type="aoe", range=4, radius=2),
        health_cost=10,
        cooldown=5,
        effects=[
            SkillEffect(effect_type="damage", magnitude=2.0, damage_type="blood"),
        ],
        tags=["BLOOD", "AOE", "SELF_DAMAGE"],
        projectile_symbol="✦",
        ai_priority=1.5,
    ),
    Skill(
        id="execution",
        name="Execution",
        description="Instantly kill an enemy below 30% HP.",
        icon="☠",
        target=SkillTarget(type="single", range=2),
        energy_cost=20,
        cooldown=6,
        effects=[
            SkillEffect(effect_type="execute", magnitude=0.3),  # Execute below 30%
        ],
        tags=["PHYSICAL", "EXECUTE", "FINISHER"],
        projectile_symbol="†",
        ai_priority=2.0,
    ),
]

# ============================================================================
# CHARACTER SKILLS - THE ASTROMANCER
# ============================================================================

ASTROMANCER_SKILLS = [
    Skill(
        id="star_bolt",
        name="Star Bolt",
        description="Fire a piercing projectile that hits all enemies in a line.",
        icon="✦",
        target=SkillTarget(type="line", range=8, width=1),
        energy_cost=12,
        cooldown=2,
        effects=[
            SkillEffect(effect_type="damage", magnitude=1.0, damage_type="void"),
        ],
        tags=["VOID", "PIERCE", "PROJECTILE"],
        projectile_symbol="✧",
        animation_duration=100,
        ai_priority=1.0,
    ),
    Skill(
        id="warp_step",
        name="Warp Step",
        description="Teleport to a target location.",
        icon="≋",
        target=SkillTarget(type="single", range=6),
        energy_cost=18,
        cooldown=3,
        effects=[
            SkillEffect(effect_type="teleport_self"),
        ],
        tags=["VOID", "TELEPORT", "MOBILITY"],
        projectile_symbol="≈",
        ai_priority=0.5,  # Defensive
    ),
    Skill(
        id="echo_seal",
        name="Echo Seal",
        description="Mark a skill to repeat after 2 turns.",
        icon="⟲",
        target=SkillTarget(type="self"),
        energy_cost=8,
        cooldown=4,
        effects=[
            SkillEffect(effect_type="echo", duration=2),
        ],
        tags=["VOID", "ECHO", "BUFF"],
        ai_priority=0.7,
    ),
    Skill(
        id="collapse",
        name="Collapse",
        description="Trigger all echo effects immediately.",
        icon="☄",
        target=SkillTarget(type="self"),
        energy_cost=25,
        cooldown=7,
        effects=[
            SkillEffect(effect_type="trigger_echos"),
            SkillEffect(effect_type="damage", magnitude=1.5, damage_type="void"),
        ],
        tags=["VOID", "ECHO", "NUKE"],
        ai_priority=1.8,
    ),
]

# ============================================================================
# CHARACTER SKILLS - THE PLAGUE SAINT
# ============================================================================

PLAGUE_SAINT_SKILLS = [
    Skill(
        id="rot_touch",
        name="Rot Touch",
        description="Touch an enemy to poison them.",
        icon="☣",
        target=SkillTarget(type="single", range=2),
        energy_cost=8,
        cooldown=2,
        effects=[
            SkillEffect(effect_type="damage", magnitude=0.7, damage_type="poison"),
            SkillEffect(effect_type="status", status_effect="poison", duration=4),
        ],
        tags=["POISON", "MELEE", "DOT"],
        ai_priority=1.0,
    ),
    Skill(
        id="spore_cloud",
        name="Spore Cloud",
        description="Create a cloud that poisons enemies who enter.",
        icon="☁",
        target=SkillTarget(type="aoe", range=5, radius=2),
        energy_cost=16,
        cooldown=5,
        effects=[
            SkillEffect(effect_type="status", status_effect="poison", duration=3),
            SkillEffect(effect_type="create_zone", duration=4),
        ],
        tags=["POISON", "AOE", "ZONE"],
        projectile_symbol="░",
        ai_priority=0.9,
    ),
    Skill(
        id="harvest",
        name="Harvest",
        description="Explode all poisoned enemies, spreading infection.",
        icon="✂",
        target=SkillTarget(type="all_poisoned"),
        energy_cost=20,
        cooldown=6,
        effects=[
            SkillEffect(effect_type="damage", magnitude=1.3, damage_type="poison"),
            SkillEffect(effect_type="spread_poison", radius=2),
        ],
        tags=["POISON", "EXPLOSION", "SPREAD"],
        ai_priority=1.4,
    ),
    Skill(
        id="bloom",
        name="Bloom",
        description="Cause mass mutation - all enemies take damage over time.",
        icon="❀",
        target=SkillTarget(type="all_enemies"),
        energy_cost=30,
        cooldown=8,
        effects=[
            SkillEffect(effect_type="damage", magnitude=0.8, damage_type="poison"),
            SkillEffect(effect_type="status", status_effect="poison", duration=5, stacks=True),
        ],
        tags=["POISON", "GLOBAL", "ULTIMATE"],
        ai_priority=2.0,
    ),
]

# ============================================================================
# CHARACTER SKILLS - THE MIRROR DUELIST
# ============================================================================

MIRROR_DUELIST_SKILLS = [
    Skill(
        id="feint",
        name="Feint",
        description="Your next attack is guaranteed to crit.",
        icon="🎭",
        target=SkillTarget(type="self"),
        energy_cost=10,
        cooldown=3,
        effects=[
            SkillEffect(effect_type="buff", status_effect="guaranteed_crit", duration=1),
        ],
        tags=["PHYSICAL", "CRIT", "BUFF"],
        ai_priority=1.1,
    ),
    Skill(
        id="mirror_step",
        name="Mirror Step",
        description="Dash through enemies, leaving an illusion behind.",
        icon="⇆",
        target=SkillTarget(type="line", range=4, width=1),
        energy_cost=14,
        cooldown=3,
        effects=[
            SkillEffect(effect_type="dash"),
            SkillEffect(effect_type="create_illusion", duration=2),
        ],
        tags=["PHYSICAL", "DASH", "ILLUSION"],
        projectile_symbol="»",
        animation_duration=80,
        ai_priority=0.8,
    ),
    Skill(
        id="riposte",
        name="Riposte",
        description="Enter a stance that counters the next attack.",
        icon="🛡",
        target=SkillTarget(type="self"),
        energy_cost=12,
        cooldown=4,
        effects=[
            SkillEffect(effect_type="stance", status_effect="riposte", duration=2),
        ],
        tags=["PHYSICAL", "COUNTER", "STANCE"],
        ai_priority=0.6,  # Defensive
    ),
    Skill(
        id="perfect_reflection",
        name="Perfect Reflection",
        description="Reflect the next enemy skill back at them.",
        icon="◈",
        target=SkillTarget(type="self"),
        energy_cost=22,
        cooldown=7,
        effects=[
            SkillEffect(effect_type="reflect", duration=1),
        ],
        tags=["VOID", "REFLECT", "COUNTER"],
        ai_priority=1.3,
    ),
]

# ============================================================================
# ENEMY SKILLS
# ============================================================================

ENEMY_SKILLS = [
    # Zombie - basic melee
    Skill(
        id="zombie_slam",
        name="Slam",
        description="Basic melee attack.",
        target=SkillTarget(type="single", range=1),
        energy_cost=0,
        cooldown=1,
        effects=[
            SkillEffect(effect_type="damage", magnitude=0.8, damage_type="physical"),
        ],
        tags=["PHYSICAL", "MELEE"],
        ai_priority=1.0,
    ),
    # Spitter - ranged poison
    Skill(
        id="spit_acid",
        name="Spit Acid",
        description="Ranged poison attack.",
        target=SkillTarget(type="single", range=5),
        energy_cost=5,
        cooldown=2,
        effects=[
            SkillEffect(effect_type="damage", magnitude=0.6, damage_type="poison"),
            SkillEffect(effect_type="status", status_effect="poison", duration=2),
        ],
        tags=["POISON", "RANGED", "DOT"],
        projectile_symbol="~",
        ai_priority=1.2,
    ),
    # Knight - defensive strike
    Skill(
        id="knight_strike",
        name="Shield Strike",
        description="Powerful strike with bonus defense.",
        target=SkillTarget(type="single", range=1),
        energy_cost=8,
        cooldown=2,
        effects=[
            SkillEffect(effect_type="damage", magnitude=1.3, damage_type="physical"),
            SkillEffect(effect_type="buff", status_effect="defense_up", duration=2),
        ],
        tags=["PHYSICAL", "MELEE", "BUFF"],
        ai_priority=1.1,
    ),
    # Necromancer - summon and curse
    Skill(
        id="summon_minion",
        name="Summon Minion",
        description="Raise a zombie from the dead.",
        target=SkillTarget(type="self"),
        energy_cost=15,
        cooldown=5,
        effects=[
            SkillEffect(effect_type="summon", summon_type="zombie"),
        ],
        tags=["VOID", "SUMMON"],
        ai_priority=0.9,
    ),
    Skill(
        id="curse_weakness",
        name="Curse of Weakness",
        description="Reduce enemy damage.",
        target=SkillTarget(type="single", range=6),
        energy_cost=10,
        cooldown=4,
        effects=[
            SkillEffect(effect_type="status", status_effect="weakness", duration=3),
        ],
        tags=["VOID", "DEBUFF"],
        projectile_symbol="☤",
        ai_priority=0.8,
    ),
]

# ============================================================================
# BOSS SKILLS
# ============================================================================

BOSS_SKILLS = [
    # The Hollow King
    Skill(
        id="hollow_strike",
        name="Hollow Strike",
        description="Devastating melee combo.",
        target=SkillTarget(type="cone", range=3, width=3),
        energy_cost=0,
        cooldown=2,
        effects=[
            SkillEffect(effect_type="damage", magnitude=1.5, damage_type="void"),
        ],
        tags=["VOID", "MELEE", "AOE"],
        ai_priority=1.3,
    ),
    Skill(
        id="mirror_clone",
        name="Mirror Clone",
        description="Create a shadow clone of yourself.",
        target=SkillTarget(type="self"),
        energy_cost=0,
        cooldown=6,
        effects=[
            SkillEffect(effect_type="summon", summon_type="clone"),
        ],
        tags=["VOID", "SUMMON", "CLONE"],
        ai_priority=1.0,
    ),
    Skill(
        id="darkness_field",
        name="Darkness Field",
        description="Fill the arena with damaging darkness.",
        target=SkillTarget(type="all_enemies"),
        energy_cost=0,
        cooldown=5,
        effects=[
            SkillEffect(effect_type="damage", magnitude=0.8, damage_type="void"),
            SkillEffect(effect_type="status", status_effect="blind", duration=2),
        ],
        tags=["VOID", "GLOBAL", "AOE"],
        ai_priority=1.4,
    ),
    # The Bell Saint
    Skill(
        id="bell_chime",
        name="Bell Chime",
        description="Ring the bell, stunning all enemies.",
        target=SkillTarget(type="all_enemies"),
        energy_cost=0,
        cooldown=4,
        effects=[
            SkillEffect(effect_type="damage", magnitude=0.5, damage_type="lightning"),
            SkillEffect(effect_type="status", status_effect="stun", duration=1),
        ],
        tags=["LIGHTNING", "GLOBAL", "STUN"],
        ai_priority=1.5,
    ),
    Skill(
        id="curse_field",
        name="Curse Field",
        description="Create zones of cursed ground.",
        target=SkillTarget(type="aoe", range=8, radius=2),
        energy_cost=0,
        cooldown=3,
        effects=[
            SkillEffect(effect_type="create_zone", zone_type="curse", duration=4),
        ],
        tags=["VOID", "ZONE"],
        projectile_symbol="§",
        ai_priority=0.9,
    ),
    # Choir of Teeth
    Skill(
        id="wall_shift",
        name="Wall Shift",
        description="Move arena walls, crushing enemies.",
        target=SkillTarget(type="line", range=10, width=1),
        energy_cost=0,
        cooldown=4,
        effects=[
            SkillEffect(effect_type="terrain_damage", magnitude=2.0),
            SkillEffect(effect_type="knockback", magnitude=2),
        ],
        tags=["PHYSICAL", "TERRAIN", "AOE"],
        ai_priority=1.2,
    ),
]

# ============================================================================
# SKILL REGISTRY
# ============================================================================

ALL_SKILLS: dict[str, Skill] = {}

def register_skills() -> None:
    """Register all skills in the global registry."""
    all_skill_lists = [
        EXECUTIONER_SKILLS,
        ASTROMANCER_SKILLS,
        PLAGUE_SAINT_SKILLS,
        MIRROR_DUELIST_SKILLS,
        ENEMY_SKILLS,
        BOSS_SKILLS,
    ]
    
    for skill_list in all_skill_lists:
        for skill in skill_list:
            ALL_SKILLS[skill.id] = skill


def get_skill(skill_id: str) -> Skill | None:
    """Get a skill by ID."""
    return ALL_SKILLS.get(skill_id)


def get_skills_by_tag(tag: str) -> list[Skill]:
    """Get all skills with a specific tag."""
    return [s for s in ALL_SKILLS.values() if tag in s.tags]


# Auto-register on import
register_skills()
