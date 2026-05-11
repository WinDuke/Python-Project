"""Core game constants for TURNBOUND."""

# Screen dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 24

# Arena dimensions
ARENA_WIDTH = 50
ARENA_HEIGHT = 25

# UI panel heights
HUD_HEIGHT = 8
COMBAT_LOG_HEIGHT = 6

# Game timing
BASE_FPS = 30
TICK_RATE = 1 / BASE_FPS

# Animation durations (ms)
ANIM_DURATION_MIN = 80
ANIM_DURATION_MAX = 250
ANIM_PROJECTILE = 150
ANIM_EXPLOSION = 200
ANIM_IMPACT = 100

# Combat constants
BASE_CRIT_CHANCE = 0.05
BASE_CRIT_MULTIPLIER = 2.0
BASE_ENERGY = 30
BASE_HP = 50

# Wave system
BASE_THREAT_BUDGET = 10
THREAT_SCALING = 1.15  # 15% increase per wave
BOSS_WAVE_INTERVAL = 5

# Entity component flags
COMP_POSITION = 1 << 0
COMP_RENDERABLE = 1 << 1
COMP_HEALTH = 1 << 2
COMP_ENERGY = 1 << 3
COMP_STATS = 1 << 4
COMP_SKILLS = 1 << 5
COMP_COOLDOWNS = 1 << 6
COMP_AI = 1 << 7
COMP_STATUSES = 1 << 8
COMP_TAGS = 1 << 9
COMP_FACTION = 1 << 10

# Faction IDs
FACTION_PLAYER = 0
FACTION_ENEMY = 1
FACTION_NEUTRAL = 2

# Damage types
DAMAGE_PHYSICAL = "physical"
DAMAGE_FIRE = "fire"
DAMAGE_FROST = "frost"
DAMAGE_LIGHTNING = "lightning"
DAMAGE_VOID = "void"
DAMAGE_POISON = "poison"
DAMAGE_BLOOD = "blood"

# Status effect types
STATUS_BURN = "burn"
STATUS_POISON = "poison"
STATUS_SHOCK = "shock"
STATUS_FREEZE = "freeze"
STATUS_BLEED = "bleed"
STATUS_VULNERABLE = "vulnerable"
STATUS_WEAKNESS = "weakness"

# Upgrade rarities
RARITY_COMMON = "common"
RARITY_RARE = "rare"
RARITY_EPIC = "epic"
RARITY_LEGENDARY = "legendary"

# Input mappings
INPUT_MOVE_UP = "up"
INPUT_MOVE_DOWN = "down"
INPUT_MOVE_LEFT = "left"
INPUT_MOVE_RIGHT = "right"
INPUT_WAIT = "wait"
INPUT_SKILL_Q = "skill_q"
INPUT_SKILL_W = "skill_w"
INPUT_SKILL_E = "skill_e"
INPUT_SKILL_R = "skill_r"
INPUT_INSPECT = "inspect"
INPUT_PAUSE = "pause"

# Render layers
LAYER_TERRAIN = 0
LAYER_OBJECTS = 1
LAYER_UNITS = 2
LAYER_EFFECTS = 3
LAYER_PARTICLES = 4
LAYER_UI = 5

# Tile types
TILE_EMPTY = "."
TILE_WALL = "#"
TILE_FLOOR = "·"
TILE_OBSTACLE = "▓"
TILE_HAZARD = "☠"

# Direction vectors
DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
    "up_left": (-1, -1),
    "up_right": (1, -1),
    "down_left": (-1, 1),
    "down_right": (1, 1),
}
