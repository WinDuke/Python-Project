"""Upgrade definitions and tag-based synergy system."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
import random


@dataclass
class UpgradeEffect:
    """A single effect granted by an upgrade."""
    type: str  # stat_mod, new_skill, mechanic_change, trigger, etc.
    target: str  # What it affects (e.g., "fire_damage", "dash", "crit")
    magnitude: float = 1.0
    description: str = ""
    condition: Optional[str] = None  # For conditional effects
    trigger: Optional[str] = None  # Trigger event for stacking buffs
    reset: Optional[str] = None  # Reset condition for stacking buffs


@dataclass
class Upgrade:
    """Complete upgrade definition."""
    id: str
    name: str
    description: str
    rarity: str  # common, rare, epic, legendary
    
    # Tags that define synergies
    tags: List[str] = field(default_factory=list)
    
    # Effects granted
    effects: List[UpgradeEffect] = field(default_factory=list)
    
    # Prerequisites (tags player must have)
    required_tags: List[str] = field(default_factory=list)
    
    # Conflicts (upgrades that can't coexist)
    conflicting_upgrades: List[str] = field(default_factory=list)
    
    # Weight for random selection (higher = more common)
    weight: int = 100
    
    # Flavor text
    flavor: str = ""


# ============================================================================
# COMMON UPGRADES
# ============================================================================

COMMON_UPGRADES = [
    Upgrade(
        id="sharp_edges",
        name="Sharp Edges",
        description="+10% physical damage",
        rarity="common",
        tags=["PHYSICAL"],
        effects=[
            UpgradeEffect(type="stat_mod", target="physical_damage", magnitude=1.10),
        ],
        flavor="A whetstone and a steady hand.",
    ),
    Upgrade(
        id="burning_ammo",
        name="Burning Ammo",
        description="Physical attacks have 20% chance to apply Burn",
        rarity="common",
        tags=["PHYSICAL", "FIRE"],
        effects=[
            UpgradeEffect(type="trigger", target="on_hit", magnitude=0.20, description="apply burn"),
        ],
        flavor="Hot lead leaves hot wounds.",
    ),
    Upgrade(
        id="quick_draw",
        name="Quick Draw",
        description="-1 cooldown on all skills (min 1)",
        rarity="common",
        tags=["UTILITY"],
        effects=[
            UpgradeEffect(type="cooldown_reduction", target="all", magnitude=-1),
        ],
        flavor="Speed kills.",
    ),
    Upgrade(
        id="thick_skin",
        name="Thick Skin",
        description="+5 Defense",
        rarity="common",
        tags=["DEFENSE"],
        effects=[
            UpgradeEffect(type="stat_mod", target="defense", magnitude=5),
        ],
        flavor="Calloused from countless battles.",
    ),
    Upgrade(
        id="vitality",
        name="Vitality",
        description="+20 Max HP",
        rarity="common",
        tags=["HEALTH"],
        effects=[
            UpgradeEffect(type="stat_mod", target="max_hp", magnitude=20),
        ],
        flavor="The will to endure.",
    ),
    Upgrade(
        id="energy_drink",
        name="Energy Drink",
        description="+10 Max Energy",
        rarity="common",
        tags=["ENERGY"],
        effects=[
            UpgradeEffect(type="stat_mod", target="max_energy", magnitude=10),
        ],
        flavor="Tastes like lightning.",
    ),
    Upgrade(
        id="keen_eye",
        name="Keen Eye",
        description="+5% Crit Chance",
        rarity="common",
        tags=["CRIT"],
        effects=[
            UpgradeEffect(type="stat_mod", target="crit_chance", magnitude=0.05),
        ],
        flavor="Nothing escapes your gaze.",
    ),
    Upgrade(
        id="murderous_intent",
        name="Murderous Intent",
        description="+10% Crit Damage",
        rarity="common",
        tags=["CRIT"],
        effects=[
            UpgradeEffect(type="stat_mod", target="crit_multiplier", magnitude=0.10),
        ],
        flavor="You don't miss vital spots by accident.",
    ),
    Upgrade(
        id="poison_coating",
        name="Poison Coating",
        description="Attacks apply weak Poison (1 stack)",
        rarity="common",
        tags=["POISON"],
        effects=[
            UpgradeEffect(type="trigger", target="on_hit", description="apply poison 1 stack"),
        ],
        flavor="Fair fights are for the unprepared.",
    ),
    Upgrade(
        id="frostbite",
        name="Frostbite",
        description="Crits have 25% chance to Freeze",
        rarity="common",
        tags=["FROST", "CRIT"],
        effects=[
            UpgradeEffect(type="trigger", target="on_crit", magnitude=0.25, description="apply freeze"),
        ],
        flavor="Cold hands, cold heart.",
    ),
]

# ============================================================================
# RARE UPGRADES
# ============================================================================

RARE_UPGRADES = [
    Upgrade(
        id="executioner_habit",
        name="Executioner's Habit",
        description="Enemies below 20% HP take +50% damage",
        rarity="rare",
        tags=["PHYSICAL", "EXECUTE"],
        required_tags=["PHYSICAL"],
        effects=[
            UpgradeEffect(type="damage_mod", target="low_hp_enemies", magnitude=1.50),
        ],
        flavor="Finish them quickly. Others are waiting.",
    ),
    Upgrade(
        id="blood_pact",
        name="Blood Pact",
        description="Losing HP restores 5 Energy",
        rarity="rare",
        tags=["BLOOD", "ENERGY"],
        required_tags=["BLOOD"],
        effects=[
            UpgradeEffect(type="trigger", target="on_damage_taken", description="restore 5 energy"),
        ],
        flavor="Pain is just power in disguise.",
    ),
    Upgrade(
        id="echo_chamber",
        name="Echo Chamber",
        description="Echoed skills cost 50% less energy",
        rarity="rare",
        tags=["VOID", "ECHO"],
        required_tags=["ECHO"],
        effects=[
            UpgradeEffect(type="cost_reduction", target="echo_skills", magnitude=0.50),
        ],
        flavor="The sound of your own greatness, repeated.",
    ),
    Upgrade(
        id="plague_doctor",
        name="Plague Doctor",
        description="Poisoned enemies heal you when they die",
        rarity="rare",
        tags=["POISON", "HEALTH"],
        required_tags=["POISON"],
        effects=[
            UpgradeEffect(type="trigger", target="on_poisoned_enemy_death", description="heal 5 HP"),
        ],
        flavor="First, do harm. Then, profit.",
    ),
    Upgrade(
        id="mirror_image",
        name="Mirror Image",
        description="Dashing creates a decoy that explodes",
        rarity="rare",
        tags=["DASH", "ILLUSION"],
        required_tags=["DASH"],
        effects=[
            UpgradeEffect(type="trigger", target="on_dash", description="create exploding decoy"),
        ],
        flavor="Which one is real? Does it matter?",
    ),
    Upgrade(
        id="lightning_rod",
        name="Lightning Rod",
        description="Shock spreads to 2 nearby enemies",
        rarity="rare",
        tags=["LIGHTNING"],
        required_tags=["LIGHTNING"],
        effects=[
            UpgradeEffect(type="spread", target="shock", magnitude=2),
        ],
        flavor="Share the pain.",
    ),
    Upgrade(
        id="berserker_rage",
        name="Berserker Rage",
        description="Below 30% HP: +40% Power but -50% Defense",
        rarity="rare",
        tags=["BLOOD", "POWER"],
        effects=[
            UpgradeEffect(type="conditional_stat", target="power", magnitude=1.40, condition="hp_below_30"),
            UpgradeEffect(type="conditional_stat", target="defense", magnitude=0.50, condition="hp_below_30"),
        ],
        flavor="Injury is temporary. Glory is forever.",
    ),
    Upgrade(
        id="tactical_retreat",
        name="Tactical Retreat",
        description="Moving away from enemies grants 1 turn of Defense +3",
        rarity="rare",
        tags=["DEFENSE", "MOBILITY"],
        effects=[
            UpgradeEffect(type="trigger", target="on_move_away", description="buff defense"),
        ],
        flavor="Living to fight another day.",
    ),
]

# ============================================================================
# EPIC UPGRADES
# ============================================================================

EPIC_UPGRADES = [
    Upgrade(
        id="inferno_core",
        name="Inferno Core",
        description="Burn explosions create firestorms that persist for 2 turns",
        rarity="epic",
        tags=["FIRE", "AOE"],
        required_tags=["FIRE", "AOE"],
        effects=[
            UpgradeEffect(type="mechanic_change", target="burn_explosion", description="create firestorm"),
        ],
        flavor="You carry a star in your chest.",
    ),
    Upgrade(
        id="time_dilation",
        name="Time Dilation",
        description="Echoes can now echo themselves (recursive echoes)",
        rarity="epic",
        tags=["VOID", "ECHO"],
        required_tags=["ECHO", "VOID"],
        effects=[
            UpgradeEffect(type="mechanic_change", target="echo_system", description="recursive echoes"),
        ],
        flavor="Past meets future meets past meets future...",
    ),
    Upgrade(
        id="pandemic",
        name="Pandemic",
        description="Poison spreads automatically every turn to adjacent enemies",
        rarity="epic",
        tags=["POISON", "SPREAD"],
        required_tags=["POISON"],
        effects=[
            UpgradeEffect(type="auto_spread", target="poison", magnitude=1),
        ],
        flavor="No quarantine can contain this.",
    ),
    Upgrade(
        id="perfect_form",
        name="Perfect Form",
        description="Counter attacks deal 200% damage and reset counter cooldown",
        rarity="epic",
        tags=["COUNTER", "CRIT"],
        required_tags=["COUNTER"],
        effects=[
            UpgradeEffect(type="damage_mod", target="counter_attacks", magnitude=2.0),
            UpgradeEffect(type="cooldown_reset", target="counter_skill"),
        ],
        flavor="Flawless. Unmatchable. Complete.",
    ),
    Upgrade(
        id="void_walker",
        name="Void Walker",
        description="Teleporting damages all enemies within 3 tiles (50% power)",
        rarity="epic",
        tags=["VOID", "TELEPORT"],
        required_tags=["TELEPORT"],
        effects=[
            UpgradeEffect(type="trigger", target="on_teleport", description="aoe damage"),
        ],
        flavor="Space bends around you. Reality complains.",
    ),
    Upgrade(
        id="carnage",
        name="Carnage",
        description="Killing an enemy resets one random skill cooldown",
        rarity="epic",
        tags=["KILL", "UTILITY"],
        effects=[
            UpgradeEffect(type="trigger", target="on_kill", description="reset random cooldown"),
        ],
        flavor="The slaughter fuels itself.",
    ),
]

# ============================================================================
# LEGENDARY UPGRADES
# ============================================================================

LEGENDARY_UPGRADES = [
    Upgrade(
        id="phoenix_engine",
        name="Phoenix Engine",
        description="Burn explosions create massive firestorms. You cannot die from HP damage while burning (1 per run).",
        rarity="legendary",
        tags=["FIRE", "AOE", "SURVIVAL"],
        required_tags=["FIRE", "AOE"],
        effects=[
            UpgradeEffect(type="mechanic_change", target="burn_explosion", magnitude=3.0, description="massive firestorm"),
            UpgradeEffect(type="survival", target="once_per_run", description="cheat death while burning"),
        ],
        flavor="From ash, you rise. Again. And again.",
        weight=10,
    ),
    Upgrade(
        id="echo_cascade",
        name="Echo Cascade",
        description="Repeated spells can repeat again. Echoes stack infinitely.",
        rarity="legendary",
        tags=["VOID", "ECHO", "INFINITE"],
        required_tags=["ECHO", "VOID"],
        effects=[
            UpgradeEffect(type="mechanic_change", target="echo_system", description="infinite stacking"),
        ],
        flavor="The universe hears you. And repeats you. Forever.",
        weight=10,
    ),
    Upgrade(
        id="crimson_reactor",
        name="Crimson Reactor",
        description="Taking damage restores Energy equal to 50% of damage taken. Skills cost HP instead of Energy.",
        rarity="legendary",
        tags=["BLOOD", "ENERGY", "TRANSFORM"],
        required_tags=["BLOOD"],
        effects=[
            UpgradeEffect(type="resource_swap", target="hp_for_energy"),
            UpgradeEffect(type="trigger", target="on_damage_taken", magnitude=0.50, description="restore energy"),
        ],
        flavor="Your heart is a furnace. Your blood, its fuel.",
        weight=10,
    ),
    Upgrade(
        id="glass_momentum",
        name="Glass Momentum",
        description="Every dodge increases Crit Damage by 50% (stacks). Taking damage resets stacks.",
        rarity="legendary",
        tags=["CRIT", "DODGE", "SNOWBALL"],
        required_tags=["CRIT"],
        effects=[
            UpgradeEffect(type="stacking_buff", target="crit_damage", magnitude=0.50, trigger="on_dodge", reset="on_damage"),
        ],
        flavor="Untouchable. Unstoppable. Until you're not.",
        weight=10,
    ),
    Upgrade(
        id="apocalypse_bloom",
        name="Apocalypse Bloom",
        description="When enemies die from Poison, they explode dealing 100% of their max HP as damage",
        rarity="legendary",
        tags=["POISON", "EXPLOSION", "CHAIN"],
        required_tags=["POISON"],
        effects=[
            UpgradeEffect(type="trigger", target="on_poison_death", magnitude=1.0, description="max_hp explosion"),
        ],
        flavor="Death blooms into death blooms into death.",
        weight=10,
    ),
    Upgrade(
        id="omniscient_blade",
        name="Omniscient Blade",
        description="You always crit. Crit multiplier becomes 1.5x. Attacks hit all enemies in range.",
        rarity="legendary",
        tags=["CRIT", "AOE", "TRANSFORM"],
        required_tags=["CRIT", "PHYSICAL"],
        effects=[
            UpgradeEffect(type="stat_mod", target="crit_chance", magnitude=1.0),
            UpgradeEffect(type="stat_mod", target="crit_multiplier", magnitude=1.5),
            UpgradeEffect(type="mechanic_change", target="attack_pattern", description="hit_all_in_range"),
        ],
        flavor="You see every weakness. Every flaw. Every ending.",
        weight=10,
    ),
]

# ============================================================================
# UPGRADE REGISTRY AND UTILITIES
# ============================================================================

ALL_UPGRADES: dict[str, Upgrade] = {}


def register_upgrades() -> None:
    """Register all upgrades."""
    all_lists = [
        COMMON_UPGRADES,
        RARE_UPGRADES,
        EPIC_UPGRADES,
        LEGENDARY_UPGRADES,
    ]
    for upgrade_list in all_lists:
        for upgrade in upgrade_list:
            ALL_UPGRADES[upgrade.id] = upgrade


def get_upgrade(upgrade_id: str) -> Upgrade | None:
    """Get an upgrade by ID."""
    return ALL_UPGRADES.get(upgrade_id)


def get_upgrades_by_rarity(rarity: str) -> list[Upgrade]:
    """Get all upgrades of a specific rarity."""
    return [u for u in ALL_UPGRADES.values() if u.rarity == rarity]


def get_upgrades_by_tag(tag: str) -> list[Upgrade]:
    """Get all upgrades with a specific tag."""
    return [u for u in ALL_UPGRADES.values() if tag in u.tags]


def generate_upgrade_choices(
    player_tags: set[str],
    owned_upgrades: set[str],
    num_choices: int = 3,
    current_wave: int = 1,
) -> list[Upgrade]:
    """Generate upgrade choices based on player state."""
    
    # Calculate rarity weights based on wave progression
    # More rare upgrades appear later
    rarity_weights = {
        "common": 100,
        "rare": 50,
        "epic": 15,
        "legendary": 5,
    }
    
    # Adjust weights based on wave
    if current_wave >= 5:
        rarity_weights["rare"] = 70
    if current_wave >= 10:
        rarity_weights["epic"] = 25
    if current_wave >= 15:
        rarity_weights["legendary"] = 10
    
    # Filter valid upgrades
    valid_upgrades = []
    for upgrade in ALL_UPGRADES.values():
        # Skip already owned
        if upgrade.id in owned_upgrades:
            continue
        
        # Skip conflicting
        conflict = False
        for conflict_id in upgrade.conflicting_upgrades:
            if conflict_id in owned_upgrades:
                conflict = True
                break
        if conflict:
            continue
        
        # Check requirements
        if upgrade.required_tags:
            if not player_tags.intersection(upgrade.required_tags):
                continue
        
        valid_upgrades.append((upgrade, rarity_weights.get(upgrade.rarity, 50)))
    
    if not valid_upgrades:
        # Fallback to any common upgrade
        valid_upgrades = [(u, 100) for u in COMMON_UPGRADES if u.id not in owned_upgrades]
    
    # Weighted random selection
    choices = []
    available = valid_upgrades.copy()
    
    for _ in range(num_choices):
        if not available:
            break
        
        total_weight = sum(w for _, w in available)
        roll = random.randint(1, total_weight)
        
        cumulative = 0
        selected_idx = 0
        for idx, (upgrade, weight) in enumerate(available):
            cumulative += weight
            if roll <= cumulative:
                selected_idx = idx
                break
        
        selected_upgrade, _ = available.pop(selected_idx)
        choices.append(selected_upgrade)
    
    return choices


# Auto-register
register_upgrades()
