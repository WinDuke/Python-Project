"""Wave system for enemy spawning and difficulty scaling."""

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional

from src.core.constants import BASE_THREAT_BUDGET, THREAT_SCALING

if TYPE_CHECKING:
    from src.ecs.entity_manager import EntityManager


@dataclass
class EnemyTemplate:
    """Template for enemy creation."""
    entity_type: str
    threat_cost: int
    count: int = 1
    min_wave: int = 1
    max_wave: int = 999


@dataclass
class WaveConfig:
    """Configuration for a single wave."""
    wave_number: int
    threat_budget: int
    enemies: List[EnemyTemplate] = field(default_factory=list)
    is_boss_wave: bool = False
    boss_type: Optional[str] = None


@dataclass
class WaveState:
    """Current state of wave progression."""
    current_wave: int = 1
    enemies_spawned: int = 0
    enemies_remaining: int = 0
    is_boss_active: bool = False
    wave_complete: bool = False


class WaveDirector:
    """Manages wave spawning and difficulty scaling."""

    def __init__(self, entity_manager: "EntityManager"):
        self.em = entity_manager
        self.state = WaveState()
        self._enemy_templates: Dict[str, EnemyTemplate] = {}
        self._rng = random.Random()
        
        # Auto-register all enemies from content
        self._auto_register_enemies()
    
    def _auto_register_enemies(self) -> None:
        """Automatically register all enemy types from content."""
        from src.content.enemies import ALL_ENEMIES
        
        for enemy_id, enemy_data in ALL_ENEMIES.items():
            template = EnemyTemplate(
                entity_type=enemy_id,
                threat_cost=enemy_data.threat_cost,
                min_wave=1,
                max_wave=999,
            )
            self.register_enemy(template)

    def register_enemy(self, template: EnemyTemplate) -> None:
        """Register an enemy type for wave generation."""
        self._enemy_templates[template.entity_type] = template

    def generate_wave(self, wave_number: int) -> WaveConfig:
        """Generate wave configuration based on wave number."""
        # Calculate threat budget with scaling
        budget = int(BASE_THREAT_BUDGET * (THREAT_SCALING ** (wave_number - 1)))

        config = WaveConfig(
            wave_number=wave_number,
            threat_budget=budget,
        )

        # Check if boss wave
        if wave_number % 5 == 0:
            config.is_boss_wave = True
            config.threat_budget = 0  # No normal enemies in boss waves
            return config

        # Generate enemy composition
        remaining_budget = budget
        available_enemies = [
            t for t in self._enemy_templates.values()
            if t.min_wave <= wave_number <= t.max_wave
        ]

        while remaining_budget > 0 and available_enemies:
            # Pick random enemy type
            template = self._rng.choice(available_enemies)

            if template.threat_cost <= remaining_budget:
                config.enemies.append(template)
                remaining_budget -= template.threat_cost
            else:
                # Remove too expensive enemies
                available_enemies.remove(template)

        return config

    def spawn_wave(
        self,
        arena_spawn_points: List[tuple[int, int]],
        enemy_factory: callable,
    ) -> List[int]:
        """Spawn all enemies for current wave. Returns entity IDs."""
        from src.components import Position

        config = self.generate_wave(self.state.current_wave)
        spawned_ids: List[int] = []

        if config.is_boss_wave:
            self.state.is_boss_active = True
            # Boss spawning handled separately
            return spawned_ids

        spawn_index = 0
        for enemy_template in config.enemies:
            for _ in range(enemy_template.count):
                if spawn_index >= len(arena_spawn_points):
                    spawn_index = 0

                spawn_pos = arena_spawn_points[spawn_index]
                spawn_index += 1

                entity_id = enemy_factory(
                    enemy_template.entity_type,
                    spawn_pos[0],
                    spawn_pos[1],
                )

                if entity_id is not None:
                    spawned_ids.append(entity_id)
                    self.state.enemies_spawned += 1
                    self.state.enemies_remaining += 1

        return spawned_ids

    def on_enemy_killed(self) -> None:
        """Called when an enemy dies."""
        if self.state.enemies_remaining > 0:
            self.state.enemies_remaining -= 1

        # Check wave completion
        if self.state.enemies_remaining <= 0 and not self.state.is_boss_active:
            self.state.wave_complete = True

    def on_boss_killed(self) -> None:
        """Called when boss dies."""
        self.state.is_boss_active = False
        self.state.wave_complete = True

    def next_wave(self) -> None:
        """Advance to next wave."""
        self.state.current_wave += 1
        self.state.enemies_spawned = 0
        self.state.enemies_remaining = 0
        self.state.wave_complete = False

    def get_wave_info(self) -> Dict:
        """Get current wave information."""
        return {
            "wave": self.state.current_wave,
            "enemies_remaining": self.state.enemies_remaining,
            "is_boss_wave": self.state.current_wave % 5 == 0,
            "is_boss_active": self.state.is_boss_active,
        }

    def reset(self) -> None:
        """Reset wave state."""
        self.state = WaveState()
