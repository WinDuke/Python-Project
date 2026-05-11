"""Main game state and core loop."""

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

from src.core.event_bus import EventBus, GameEvent
from src.ecs.entity_manager import EntityManager
from src.generation.arena_generator import Arena, ArenaGenerator
from src.systems.combat_system import CombatSystem
from src.systems.movement_system import MovementSystem
from src.systems.wave_system import WaveDirector
from src.systems.upgrade_system import UpgradeSystem
from src.render.renderer import RenderSystem
from src.animation.effects import AnimationSystem

if TYPE_CHECKING:
    from src.systems.ai_system import AISystem


class GameState(Enum):
    """Game state enumeration."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    LEVEL_UP = auto()
    GAME_OVER = auto()
    VICTORY = auto()


@dataclass
class GameConfig:
    """Game configuration."""
    screen_width: int = 80
    screen_height: int = 24
    arena_width: int = 50
    arena_height: int = 25
    target_fps: int = 30


@dataclass
class PlayerData:
    """Player run data."""
    character_id: str = ""
    name: str = "Unknown"
    level: int = 1
    exp: int = 0
    kills: int = 0
    wave_reached: int = 1


class Game:
    """Main game class orchestrating all systems."""

    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()
        self.state = GameState.MENU
        self.player_data = PlayerData()

        # Core systems
        self.em = EntityManager()
        self.event_bus = EventBus()

        # Initialize systems
        self.movement_system = MovementSystem(self.em, self.event_bus)
        self.combat_system = CombatSystem(self.em, self.event_bus)
        self.render_system = RenderSystem(
            self.config.screen_width,
            self.config.screen_height
        )
        self.animation_system = AnimationSystem()

        # Arena
        self.arena_generator = ArenaGenerator(
            self.config.arena_width,
            self.config.arena_height
        )
        self.current_arena: Optional[Arena] = None

        # Wave system
        self.wave_director = WaveDirector(self.em)
        
        # Upgrade system
        self.upgrade_system: Optional[UpgradeSystem] = None

        # AI system (initialized after movement/combat)
        self.ai_system: Optional["AISystem"] = None

        # Game timing
        self._running = False
        self._turn_count = 0
        self._boss_active = False
        
        # Pending actions queue
        self._pending_actions: list[tuple[str, dict]] = []
        
        # Callback for UI updates
        self._on_turn_complete = None

        # Setup render layers
        self._setup_render_layers()

        # Subscribe to events
        self._setup_event_listeners()

    def _setup_render_layers(self) -> None:
        """Initialize render layers."""
        from src.core.constants import (
            LAYER_TERRAIN, LAYER_OBJECTS, LAYER_UNITS,
            LAYER_EFFECTS, LAYER_PARTICLES
        )

        self.render_system.register_layer("terrain", LAYER_TERRAIN)
        self.render_system.register_layer("objects", LAYER_OBJECTS)
        self.render_system.register_layer("units", LAYER_UNITS)
        self.render_system.register_layer("effects", LAYER_EFFECTS)
        self.render_system.register_layer("particles", LAYER_PARTICLES)

    def _setup_event_listeners(self) -> None:
        """Setup event listeners for game logic."""

        def on_kill(event: GameEvent) -> None:
            """Handle enemy death."""
            self.player_data.kills += 1
            self.wave_director.on_enemy_killed()

        self.event_bus.subscribe("kill", on_kill)

    def new_game(self, character_id: str, player_name: str = "Hero") -> None:
        """Start a new game."""
        self.player_data.character_id = character_id
        self.player_data.name = player_name
        self.player_data.level = 1
        self.player_data.exp = 0
        self.player_data.kills = 0
        self.player_data.wave_reached = 1

        # Generate arena
        self.current_arena = self.arena_generator.generate()

        # Set up movement system with arena obstacles
        self.movement_system.set_solid_tiles(self.current_arena.obstacles)

        # Initialize upgrade system
        self.upgrade_system = UpgradeSystem(self)
        self.combat_system.set_upgrade_system(self.upgrade_system)

        # Create player entity
        self._create_player(character_id)

        # Reset wave system
        self.wave_director.reset()

        # Spawn first wave
        self._spawn_wave()

        # Change state
        self.state = GameState.PLAYING
        self._running = True
        self._turn_count = 0
        self._boss_active = False

    def _create_player(self, character_id: str) -> None:
        """Create player entity."""
        from src.components import (
            Position, Renderable, Health, Energy, Stats,
            Skills, Cooldowns, Statuses, Faction, Tags, Level, Movement
        )
        from src.core.constants import FACTION_PLAYER
        from src.content.characters import get_character

        entity_id = self.em.create_entity()

        # Get starting position from arena
        start_pos = self.current_arena.player_start if self.current_arena else (25, 12)

        # Add components
        self.em.add_component(entity_id, Position(start_pos[0], start_pos[1]))
        self.em.add_component(entity_id, Renderable(symbol="@", color="cyan", bold=True))
        self.em.add_component(entity_id, Health(current=50, maximum=50))
        self.em.add_component(entity_id, Energy(current=30, maximum=30))
        self.em.add_component(entity_id, Stats(power=5, defense=0))
        self.em.add_component(entity_id, Skills(active_skills=["fireball"]))
        self.em.add_component(entity_id, Cooldowns())
        self.em.add_component(entity_id, Statuses())
        self.em.add_component(entity_id, Faction(faction_id=FACTION_PLAYER))
        self.em.add_component(entity_id, Tags())
        self.em.add_component(entity_id, Level())
        self.em.add_component(entity_id, Movement())

        # Apply character template if specified
        character = get_character(character_id)
        if character:
            from src.content.characters import apply_character_template
            apply_character_template(self.em, entity_id, character)

        return entity_id

    def _spawn_wave(self) -> None:
        """Spawn the current wave of enemies."""
        if not self.current_arena:
            return

        def create_enemy(enemy_type: str, x: int, y: int) -> Optional[int]:
            """Factory function to create enemies."""
            from src.components import (
                Position, Renderable, Health, Stats, AI, Faction, Cooldowns, Statuses
            )
            from src.core.constants import FACTION_ENEMY

            entity_id = self.em.create_entity()

            # Basic enemy template
            self.em.add_component(entity_id, Position(x, y))
            self.em.add_component(entity_id, Renderable(symbol="e", color="red"))
            self.em.add_component(entity_id, Health(current=20, maximum=20))
            self.em.add_component(entity_id, Stats(power=3, defense=0))
            self.em.add_component(entity_id, AI(behavior_type="aggressive"))
            self.em.add_component(entity_id, Faction(faction_id=FACTION_ENEMY))
            self.em.add_component(entity_id, Cooldowns())
            self.em.add_component(entity_id, Statuses())

            return entity_id

        self.wave_director.spawn_wave(
            self.current_arena.spawn_points,
            create_enemy
        )

    async def process_turn(self, action: str, data: dict = None) -> None:
        """Process a single turn."""
        if self.state != GameState.PLAYING:
            return

        data = data or {}

        # Process player action
        await self._process_player_action(action, data)

        # Process enemy turns
        if self.ai_system:
            self.ai_system.update_all_enemies()

        # Tick statuses for all entities
        self._tick_statuses()

        # Check wave completion
        if self.wave_director.state.wave_complete:
            self._on_wave_complete()

        # Increment turn counter
        self._turn_count += 1

        # Render
        self.render()

    async def _process_player_action(self, action: str, data: dict) -> None:
        """Process player input action."""
        from src.core.constants import DIRECTIONS
        from src.components import Position, Faction

        if action in DIRECTIONS:
            dx, dy = DIRECTIONS[action]
            player_entities = self.em.query(Position, Faction)
            for entity_id in player_entities:
                faction = self.em.get_component(entity_id, Faction)
                if faction and faction.faction_id == 0:
                    self.movement_system.move_entity(entity_id, dx, dy)
                    break

    def _tick_statuses(self) -> None:
        """Tick status effects for all entities."""
        from src.components import Statuses

        entities_with_statuses = self.em.query(Statuses)
        for entity_id in entities_with_statuses:
            self.combat_system.tick_statuses(entity_id)

    def _on_wave_complete(self) -> None:
        """Handle wave completion."""
        self.wave_director.next_wave()
        self.player_data.wave_reached = self.wave_director.state.current_wave

        # Spawn next wave after delay
        # For now, spawn immediately
        self._spawn_wave()

    def render(self) -> None:
        """Render the current game state."""
        from src.components import Position, Renderable, Faction
        
        if not self.current_arena:
            return

        # Clear layers
        for layer_name in ["terrain", "objects", "units", "effects", "particles"]:
            self.render_system.clear_layer(layer_name)

        # Render terrain
        for (x, y), tile in self.current_arena.tiles.items():
            color = "grey35" if tile == "#" else "grey50"
            self.render_system.set_tile("terrain", x, y, tile, color=color)

        # Render entities
        positions = self.em.query(Position, Renderable)
        for entity_id in positions:
            pos = self.em.get_component(entity_id, Position)
            renderable = self.em.get_component(entity_id, Renderable)

            if pos and renderable:
                self.render_system.set_tile(
                    "units",
                    pos.x, pos.y,
                    renderable.symbol,
                    color=renderable.color,
                    bold=renderable.bold,
                )

        # Center camera on player
        player_entities = self.em.query(Position, Faction)
        for entity_id in player_entities:
            faction = self.em.get_component(entity_id, Faction)
            if faction and faction.faction_id == 0:
                pos = self.em.get_component(entity_id, Position)
                if pos:
                    self.render_system.center_camera_on(pos.x, pos.y)
                    break

    def get_player_entity(self) -> Optional[int]:
        """Get the player entity ID."""
        from src.components import Faction

        factions = self.em.query(Faction)
        for entity_id in factions:
            faction = self.em.get_component(entity_id, Faction)
            if faction and faction.faction_id == 0:
                return entity_id
        return None

    def is_player_alive(self) -> bool:
        """Check if player is alive."""
        from src.components import Health, Faction

        factions = self.em.query(Health, Faction)
        for entity_id in factions:
            faction = self.em.get_component(entity_id, Faction)
            if faction and faction.faction_id == 0:
                health = self.em.get_component(entity_id, Health)
                return health and not health.is_dead
        return False

    def handle_input(self, action: str, data: dict = None) -> None:
        """Handle player input and queue for processing."""
        
        if self.state != GameState.PLAYING:
            return
        
        # Store input for processing by the async game loop
        self._pending_actions.append((action, data or {}))
    
    async def process_pending_actions(self) -> None:
        """Process all pending player actions."""
        if not self._pending_actions or self.state != GameState.PLAYING:
            return
        
        # Process one action per frame (turn-based)
        action, data = self._pending_actions.pop(0)
        await self.process_turn(action, data)
        
        # Notify UI of turn completion
        if self._on_turn_complete:
            self._on_turn_complete()

    def quit(self) -> None:
        """Quit the game."""
        self._running = False
        self.state = GameState.MENU
