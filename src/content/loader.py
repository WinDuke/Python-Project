"""Content loading system for data-driven game content."""

import json
from pathlib import Path
from typing import Any, TypeVar, Generic


T = TypeVar('T')


class ContentLoader(Generic[T]):
    """Generic content loader for JSON-based game data."""
    
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self._cache: dict[str, Any] = {}
        self._loaded = False
    
    def load_all(self) -> dict[str, Any]:
        """Load all content files from the directory."""
        if self._loaded:
            return self._cache
        
        self.directory.mkdir(parents=True, exist_ok=True)
        
        for file_path in self.directory.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    content_id = file_path.stem
                    self._cache[content_id] = data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Failed to load {file_path}: {e}")
        
        self._loaded = True
        return self._cache
    
    def get(self, content_id: str) -> Any | None:
        """Get content by ID, loading if necessary."""
        if not self._loaded:
            self.load_all()
        return self._cache.get(content_id)
    
    def save(self, content_id: str, data: Any) -> None:
        """Save content to a JSON file."""
        self.directory.mkdir(parents=True, exist_ok=True)
        file_path = self.directory / f"{content_id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        self._cache[content_id] = data
    
    def clear_cache(self) -> None:
        """Clear the loaded cache."""
        self._cache.clear()
        self._loaded = False


class GameContentLoader:
    """Centralized loader for all game content."""
    
    def __init__(self, base_dir: str | Path = "data"):
        self.base_dir = Path(base_dir)
        
        # Initialize loaders for each content type
        self.characters = ContentLoader(self.base_dir / "characters")
        self.enemies = ContentLoader(self.base_dir / "enemies")
        self.bosses = ContentLoader(self.base_dir / "bosses")
        self.skills = ContentLoader(self.base_dir / "skills")
        self.upgrades = ContentLoader(self.base_dir / "upgrades")
        self.arenas = ContentLoader(self.base_dir / "arenas")
        self.status_effects = ContentLoader(self.base_dir / "status_effects")
        self.particles = ContentLoader(self.base_dir / "particles")
    
    def load_all(self) -> None:
        """Load all content types."""
        self.characters.load_all()
        self.enemies.load_all()
        self.bosses.load_all()
        self.skills.load_all()
        self.upgrades.load_all()
        self.arenas.load_all()
        self.status_effects.load_all()
        self.particles.load_all()
    
    def get_character(self, character_id: str) -> dict | None:
        """Get character data."""
        return self.characters.get(character_id)
    
    def get_enemy(self, enemy_id: str) -> dict | None:
        """Get enemy data."""
        return self.enemies.get(enemy_id)
    
    def get_boss(self, boss_id: str) -> dict | None:
        """Get boss data."""
        return self.bosses.get(boss_id)
    
    def get_skill(self, skill_id: str) -> dict | None:
        """Get skill data."""
        return self.skills.get(skill_id)
    
    def get_upgrade(self, upgrade_id: str) -> dict | None:
        """Get upgrade data."""
        return self.upgrades.get(upgrade_id)
    
    def get_arena(self, arena_id: str) -> dict | None:
        """Get arena data."""
        return self.arenas.get(arena_id)
    
    def get_status_effect(self, effect_id: str) -> dict | None:
        """Get status effect data."""
        return self.status_effects.get(effect_id)
    
    def get_particle(self, particle_id: str) -> dict | None:
        """Get particle effect data."""
        return self.particles.get(particle_id)


# ============================================================================
# JSON SCHEMA TEMPLATES
# ============================================================================

def get_enemy_schema_template() -> dict:
    """Return a template for enemy JSON files."""
    return {
        "id": "enemy_id",
        "name": "Enemy Name",
        "description": "Description of the enemy.",
        "symbol": "e",
        "color": "red",
        "bold": False,
        "stats": {
            "hp": 20,
            "power": 3,
            "defense": 0,
            "crit_chance": 0.05,
            "crit_multiplier": 1.8,
            "speed": 1
        },
        "behavior": {
            "type": "aggressive",
            "preferred_range": 1,
            "aggression": 0.8,
            "retreat_threshold": 0.3
        },
        "threat_cost": 2,
        "skills": ["basic_attack"],
        "tags": ["TAG1", "TAG2"],
        "exp_reward": 10,
        "elite_modifier": None
    }


def get_skill_schema_template() -> dict:
    """Return a template for skill JSON files."""
    return {
        "id": "skill_id",
        "name": "Skill Name",
        "description": "Description of what the skill does.",
        "icon": "?",
        "target": {
            "type": "single",
            "range": 5,
            "radius": 0,
            "width": 0,
            "requires_line_of_sight": True
        },
        "energy_cost": 10,
        "health_cost": 0,
        "cooldown": 3,
        "effects": [
            {
                "effect_type": "damage",
                "magnitude": 1.0,
                "duration": 0,
                "damage_type": "physical"
            }
        ],
        "tags": ["TAG1", "TAG2"],
        "projectile_symbol": "*",
        "impact_symbol": "!",
        "animation_duration": 150,
        "ai_priority": 1.0
    }


def get_upgrade_schema_template() -> dict:
    """Return a template for upgrade JSON files."""
    return {
        "id": "upgrade_id",
        "name": "Upgrade Name",
        "description": "What this upgrade does.",
        "rarity": "common",
        "tags": ["TAG1"],
        "effects": [
            {
                "type": "stat_mod",
                "target": "power",
                "magnitude": 1.1,
                "description": "+10% Power"
            }
        ],
        "required_tags": [],
        "conflicting_upgrades": [],
        "weight": 100,
        "flavor": "Flavor text goes here."
    }


def get_boss_schema_template() -> dict:
    """Return a template for boss JSON files."""
    return {
        "id": "boss_id",
        "name": "Boss Name",
        "title": "The Title",
        "description": "Boss description.",
        "lore": "Lore text...",
        "symbol": "B",
        "color": "bright_red",
        "bold": True,
        "base_hp": 100,
        "base_power": 8,
        "base_defense": 2,
        "base_crit_chance": 0.10,
        "base_crit_multiplier": 2.0,
        "phases": [
            {
                "name": "Phase 1",
                "description": "First phase.",
                "symbol": "B",
                "color": "red",
                "hp_modifier": 1.0,
                "power_modifier": 1.0,
                "skills": ["boss_attack"],
                "aggression": 0.8,
                "preferred_range": 1,
                "trigger_at_hp_percent": 1.0
            }
        ],
        "mechanics": [
            {
                "name": "Special Mechanic",
                "description": "What it does.",
                "trigger_condition": "turn",
                "trigger_value": 5,
                "effect": "special_effect"
            }
        ],
        "all_skills": ["boss_attack"],
        "tags": ["BOSS", "TAG"],
        "exp_reward": 100,
        "first_appearance_wave": 5
    }


# ============================================================================
# EXPORT/IMPORT UTILITIES
# ============================================================================

def export_content_to_json(loader: GameContentLoader, output_dir: str | Path) -> None:
    """Export all in-memory content to JSON files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # This would export the Python-defined content to JSON
    # For MVP, we use Python modules directly
    pass


def import_content_from_json(loader: GameContentLoader, input_dir: str | Path) -> None:
    """Import content from JSON files into the loader."""
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        return
    
    # Load from subdirectories
    for subdir in ["characters", "enemies", "bosses", "skills", "upgrades"]:
        sub_dir = input_dir / subdir
        if sub_dir.exists():
            getattr(loader, subdir).directory = sub_dir
            getattr(loader, subdir).load_all()
