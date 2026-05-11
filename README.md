# TURNBOUND

## A Production-Ready ASCII Turn-Based Survival Roguelike

A highly stylized turn-based ASCII survival roguelike built in Python using Textual + Rich.

---

## Features

- **Tactical Roguelike Combat** - Turn-based gameplay with deep tactical decisions
- **Survival Wave Gameplay** - Survive increasingly difficult waves of enemies
- **Deep Build Crafting** - Tag-driven upgrade system with emergent synergies
- **Boss Duels** - Epic multi-phase boss encounters
- **Procedural Arenas** - Unique battlefields every run
- **Advanced ASCII Animation** - Visually impressive terminal rendering

---

## Installation

```bash
pip install textual rich pytest
```

---

## Running the Game

### Full UI Mode
```bash
python main.py
```

### CLI Demo
```bash
python main.py --demo
```

### Run Tests
```bash
python main.py --test
# or
pytest tests/ -v
```

---

## Controls

| Key | Action |
|-----|--------|
| ↑↓←→ | Move |
| Space | Wait |
| QWER | Skills |
| ESC | Pause |
| ENTER | Select |

---

## Architecture

### ECS-Lite System
- Entities are integer IDs
- Components contain only data
- Systems contain logic
- No deep inheritance trees

### Core Systems
- **Entity Manager** - Archetype-based entity storage
- **Combat System** - Damage calculations, crits, statuses
- **Movement System** - Collision detection, path validation
- **AI System** - Utility-based decision making
- **Render System** - Layered rendering with dirty tile optimization
- **Wave System** - Threat budget spawning, difficulty scaling

### Event Bus
Decoupled communication via events:
- `on_hit`, `on_crit`, `on_kill`
- `on_move`, `on_dash`
- `on_status_apply`, `on_status_remove`
- `on_levelup`, `on_wave_complete`
- `on_boss_phase_change`

---

## Project Structure

```
project/
├── assets/          # ASCII art, palettes, themes
├── data/            # JSON game content
├── saves/           # Save files
├── src/
│   ├── core/        # Game loop, constants, config
│   ├── ecs/         # Entity management
│   ├── components/  # ECS components
│   ├── systems/     # Game systems
│   ├── render/      # Rendering engine
│   ├── animation/   # Visual effects
│   ├── ai/          # AI and pathfinding
│   ├── generation/  # Procedural generation
│   ├── ui/          # Textual screens
│   └── utils/       # Utilities
├── tests/           # Pytest tests
└── main.py          # Entry point
```

---

## Characters (MVP)

1. **The Executioner** - Blood-fueled melee fighter with rage mechanics
2. **The Astromancer** - Temporal manipulation with echo system
3. **The Plague Saint** - Infection spread and arena corruption
4. **The Mirror Duelist** - Precision counters and prediction

---

## Damage Formula

```
FinalDamage = (BaseDamage + Power) × CritMultiplier - Defense
```

Modifiers include:
- Resistances
- Vulnerability
- Status interactions
- Terrain modifiers

---

## Status Effects

- **Burn** - Damage over time
- **Poison** - Stacking DOT
- **Shock** - Increases next damage
- **Freeze** - Reduces movement/skips turns
- **Bleed** - Movement causes damage
- **Vulnerable** - Take increased damage
- **Weakness** - Deal reduced damage

---

## Development Roadmap

- [x] Phase 1: Engine Core (ECS, render pipeline, input handling)
- [x] Phase 2: Combat (movement, damage, skills, statuses)
- [x] Phase 3: AI (utility AI, pathfinding, behaviors)
- [ ] Phase 4: Content (characters, enemies, arenas, bosses)
- [ ] Phase 5: Build System (upgrades, tag synergies)
- [ ] Phase 6: Polish (animations, transitions, VFX)

---

## Testing

Comprehensive test coverage for:
- Damage calculations
- Status interactions
- Wave generation
- AI scoring
- Upgrade generation

Run tests:
```bash
pytest tests/ -v
```

---

## Performance Targets

- 30+ FPS rendering
- Support 25+ simultaneous enemies
- Deterministic turn logic
- Dirty tile rendering optimization

---

## Tech Stack

- **Python 3.12+**
- **Textual** - TUI framework
- **Rich** - Terminal rendering
- **asyncio** - Async operations
- **pytest** - Testing

---

## License

MIT

---

*"A modern indie roguelike rendered entirely through terminal magic."*
