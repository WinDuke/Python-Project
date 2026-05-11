"""Main entry point for TURNBOUND."""

import asyncio
import sys


def run_game() -> None:
    """Run the game with Textual UI."""
    from src.ui.main_menu import TurnboundMenu
    
    app = TurnboundMenu()
    app.run()


def run_cli_demo() -> None:
    """Run a CLI demonstration of the game engine."""
    from src.core.game import Game, GameConfig
    from src.core.constants import ARENA_WIDTH, ARENA_HEIGHT
    
    # Create game instance
    config = GameConfig(
        screen_width=80,
        screen_height=24,
        arena_width=ARENA_WIDTH,
        arena_height=ARENA_HEIGHT,
    )
    
    game = Game(config)
    
    print("=" * 60)
    print("TURNBOUND - CLI Demo")
    print("=" * 60)
    
    # Start new game
    game.new_game("executioner", "Test Hero")
    
    print(f"\nGame started!")
    print(f"Player: {game.player_data.name}")
    print(f"Character: {game.player_data.character_id}")
    print(f"Wave: {game.wave_director.state.current_wave}")
    
    # Render initial state
    game.render()
    rendered = game.render_system.render()
    
    print("\n" + str(rendered))
    
    # Show entity count
    print(f"\nEntities created: {game.em.count()}")
    
    # Show wave info
    wave_info = game.wave_director.get_wave_info()
    print(f"\nWave Info:")
    print(f"  Current Wave: {wave_info['wave']}")
    print(f"  Enemies Remaining: {wave_info['enemies_remaining']}")
    print(f"  Is Boss Wave: {wave_info['is_boss_wave']}")
    
    print("\n" + "=" * 60)
    print("Demo complete! Run 'python main.py' for full UI.")
    print("=" * 60)


def run_tests() -> None:
    """Run pytest tests."""
    import subprocess
    subprocess.run(["pytest", "tests/", "-v"])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            run_cli_demo()
        elif sys.argv[1] == "--test":
            run_tests()
        else:
            print("Usage: python main.py [--demo|--test]")
            sys.exit(1)
    else:
        run_game()
