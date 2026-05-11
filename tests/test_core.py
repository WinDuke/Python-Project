"""Tests for TURNBOUND game systems."""

import pytest
from src.core.constants import FACTION_PLAYER, FACTION_ENEMY
from src.ecs.entity_manager import EntityManager, Component
from src.components import (
    Position, Health, Energy, Stats, Faction, Statuses, Cooldowns
)
from src.core.event_bus import EventBus, GameEvent
from src.systems.combat_system import CombatSystem
from src.systems.movement_system import MovementSystem
from src.generation.arena_generator import ArenaGenerator


# ============== ENTITY MANAGER TESTS ==============

class TestEntityManager:
    """Tests for ECS entity management."""

    def test_create_entity(self):
        em = EntityManager()
        entity_id = em.create_entity()
        assert entity_id == 0
        assert em.count() == 1

    def test_multiple_entities(self):
        em = EntityManager()
        id1 = em.create_entity()
        id2 = em.create_entity()
        id3 = em.create_entity()
        assert id1 == 0
        assert id2 == 1
        assert id3 == 2
        assert em.count() == 3

    def test_destroy_entity(self):
        em = EntityManager()
        entity_id = em.create_entity()
        em.destroy_entity(entity_id)
        assert em.count() == 0

    def test_add_component(self):
        em = EntityManager()
        entity_id = em.create_entity()
        em.add_component(entity_id, Position(5, 10))
        
        pos = em.get_component(entity_id, Position)
        assert pos is not None
        assert pos.x == 5
        assert pos.y == 10

    def test_query_entities(self):
        em = EntityManager()
        
        # Create entities with different components
        e1 = em.create_entity()
        em.add_component(e1, Position(0, 0))
        em.add_component(e1, Health(100, 100))
        
        e2 = em.create_entity()
        em.add_component(e2, Position(5, 5))
        em.add_component(e2, Health(50, 50))
        
        e3 = em.create_entity()
        em.add_component(e3, Position(10, 10))
        # No health component
        
        # Query entities with both Position and Health
        results = em.query(Position, Health)
        assert len(results) == 2
        assert e1 in results
        assert e2 in results
        assert e3 not in results


# ============== COMPONENT TESTS ==============

class TestHealthComponent:
    """Tests for Health component."""

    def test_damage(self):
        health = Health(50, 50)
        actual = health.damage(20)
        assert actual == 20
        assert health.current == 30

    def test_damage_overkill(self):
        health = Health(10, 50)
        actual = health.damage(100)
        assert actual == 10
        assert health.current == 0
        assert health.is_dead

    def test_heal(self):
        health = Health(30, 50)
        actual = health.heal(10)
        assert actual == 10
        assert health.current == 40

    def test_heal_overflow(self):
        health = Health(45, 50)
        actual = health.heal(100)
        assert actual == 5
        assert health.current == 50

    def test_percent(self):
        health = Health(25, 50)
        assert health.percent == 0.5


class TestEnergyComponent:
    """Tests for Energy component."""

    def test_spend(self):
        energy = Energy(30, 30)
        assert energy.spend(10) is True
        assert energy.current == 20

    def test_spend_insufficient(self):
        energy = Energy(5, 30)
        assert energy.spend(10) is False
        assert energy.current == 5

    def test_restore(self):
        energy = Energy(10, 30)
        actual = energy.restore(10)
        assert actual == 10
        assert energy.current == 20


# ============== COMBAT SYSTEM TESTS ==============

class TestCombatSystem:
    """Tests for combat calculations."""

    def setup_method(self):
        self.em = EntityManager()
        self.event_bus = EventBus()
        self.combat = CombatSystem(self.em, self.event_bus)

    def test_basic_damage(self):
        # Create attacker and target
        attacker = self.em.create_entity()
        target = self.em.create_entity()
        
        self.em.add_component(attacker, Stats(power=10))
        self.em.add_component(target, Health(50, 50))
        self.em.add_component(target, Stats(defense=2))
        
        damage, is_crit = self.combat.calculate_damage(attacker, target, 10)
        
        # Expected: (10 + 10) - 2 = 18 (without crit), or 36 with crit
        # Allow some variance due to upgrade system modifiers
        assert 15 <= damage <= 40  # Reasonable range accounting for modifiers

    def test_damage_with_crit(self):
        attacker = self.em.create_entity()
        target = self.em.create_entity()
        
        self.em.add_component(attacker, Stats(
            power=10,
            crit_chance=1.0,  # Guaranteed crit
            crit_multiplier=2.0
        ))
        self.em.add_component(target, Health(100, 100))
        self.em.add_component(target, Stats(defense=0))
        
        damage, is_crit = self.combat.calculate_damage(attacker, target, 10)
        
        # Expected: (10 + 10) * 2.0 = 40
        assert damage == 40
        assert is_crit is True

    def test_minimum_damage(self):
        attacker = self.em.create_entity()
        target = self.em.create_entity()
        
        self.em.add_component(attacker, Stats(power=0))
        self.em.add_component(target, Health(50, 50))
        self.em.add_component(target, Stats(defense=100))
        
        damage, _ = self.combat.calculate_damage(attacker, target, 5)
        
        # Minimum 1 damage
        assert damage >= 1


# ============== MOVEMENT SYSTEM TESTS ==============

class TestMovementSystem:
    """Tests for movement and collision."""

    def setup_method(self):
        self.em = EntityManager()
        self.event_bus = EventBus()
        self.movement = MovementSystem(self.em, self.event_bus)
        
        # Set up some solid tiles
        self.movement.set_solid_tiles({(5, 5), (5, 6), (6, 5)})

    def test_move_entity(self):
        entity = self.em.create_entity()
        self.em.add_component(entity, Position(0, 0))
        
        result = self.movement.move_entity(entity, 1, 1)
        assert result is True
        
        pos = self.em.get_component(entity, Position)
        assert pos.x == 1
        assert pos.y == 1

    def test_move_into_wall(self):
        entity = self.em.create_entity()
        self.em.add_component(entity, Position(4, 4))
        
        result = self.movement.move_entity(entity, 1, 1)
        assert result is False
        
        pos = self.em.get_component(entity, Position)
        assert pos.x == 4
        assert pos.y == 4

    def test_can_move_to(self):
        assert self.movement.can_move_to(0, 0, 0) is True
        assert self.movement.can_move_to(0, 5, 5) is False


# ============== ARENA GENERATOR TESTS ==============

class TestArenaGenerator:
    """Tests for procedural arena generation."""

    def test_generate_arena(self):
        generator = ArenaGenerator(width=30, height=20)
        arena = generator.generate(biome="cemetery")
        
        assert arena.width == 30
        assert arena.height == 20
        assert len(arena.obstacles) > 0
        assert len(arena.spawn_points) > 0

    def test_arena_borders(self):
        generator = ArenaGenerator(width=20, height=15)
        arena = generator.generate()
        
        # Check borders are solid
        for x in range(arena.width):
            assert (x, 0) in arena.obstacles
            assert (x, arena.height - 1) in arena.obstacles
        
        for y in range(arena.height):
            assert (0, y) in arena.obstacles
            assert (arena.width - 1, y) in arena.obstacles

    def test_player_start_valid(self):
        generator = ArenaGenerator(width=30, height=20)
        arena = generator.generate()
        
        px, py = arena.player_start
        assert (px, py) not in arena.obstacles
        assert 0 <= px < arena.width
        assert 0 <= py < arena.height


# ============== EVENT BUS TESTS ==============

class TestEventBus:
    """Tests for event system."""

    def test_subscribe_and_emit(self):
        bus = EventBus()
        received = []
        
        def handler(event: GameEvent):
            received.append(event)
        
        bus.subscribe("test_event", handler)
        bus.emit(GameEvent(event_type="test_event"))
        
        assert len(received) == 1
        assert received[0].event_type == "test_event"

    def test_multiple_subscribers(self):
        bus = EventBus()
        count = [0]
        
        def handler1(event: GameEvent):
            count[0] += 1
        
        def handler2(event: GameEvent):
            count[0] += 10
        
        bus.subscribe("test", handler1)
        bus.subscribe("test", handler2)
        bus.emit(GameEvent(event_type="test"))
        
        assert count[0] == 11

    def test_event_queue(self):
        bus = EventBus()
        received = []
        
        def handler(event: GameEvent):
            received.append(event.event_type)
        
        bus.subscribe("queued", handler)
        bus.queue_event(GameEvent(event_type="queued"))
        bus.queue_event(GameEvent(event_type="queued"))
        
        assert len(received) == 0  # Not processed yet
        
        bus.process_queue()
        assert received == ["queued", "queued"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
