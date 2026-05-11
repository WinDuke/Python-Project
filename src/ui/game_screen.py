"""Textual UI for TURNBOUND."""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Header, Footer, Static, Button, Label
from textual.binding import Binding
from textual.screen import Screen
from textual.reactive import reactive
from typing import Optional, Dict, Any

from src.core.game import Game, GameConfig, PlayerData
from src.core.constants import ARENA_WIDTH, ARENA_HEIGHT
from src.content.characters import ALL_CHARACTERS as CHARACTER_DATA


class TitleScreen(Screen):
    """Main title screen with animated ASCII art."""

    BINDINGS = [
        Binding("enter", "start_game", "Start Game"),
        Binding("c", "select_character", "Characters"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("""
██╗   ██╗ █████╗ ██████╗ ██╗      ██████╗  ██████╗██╗  ██╗███████╗
╚██╗ ██╔╝██╔══██╗██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝╚══███╔╝
 ╚████╔╝ ███████║██████╔╝██║     ██║   ██║██║     █████╔╝   ███╔╝ 
  ╚██╔╝  ██╔══██║██╔══██╗██║     ██║   ██║██║     ██╔═██╗  ███╔╝  
   ██║   ██║  ██║██║  ██║███████╗╚██████╔╝╚██████╗██║  ██╗███████╗
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝
            """, id="title"),
            Static("[bold red]TURNBOUND[/bold red]", id="subtitle"),
            Static("", id="decorations"),
            Vertical(
                Button("START GAME", id="btn-start", variant="primary"),
                Button("CHARACTERS", id="btn-characters"),
                Button("SETTINGS", id="btn-settings"),
                Button("EXIT", id="btn-exit"),
                id="menu",
            ),
            id="main-container",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-start":
            # Start with default character
            self.app.selected_character = "executioner"
            self.app.push_screen("game_screen")
        elif event.button.id == "btn-characters":
            self.app.push_screen("character_select")
        elif event.button.id == "btn-exit":
            self.app.exit()

    def action_start_game(self) -> None:
        self.app.selected_character = "executioner"
        self.app.push_screen("game_screen")

    def action_select_character(self) -> None:
        self.app.push_screen("character_select")

    def action_quit(self) -> None:
        self.app.exit()


class CharacterSelectScreen(Screen):
    """Character selection screen."""

    BINDINGS = [
        Binding("up", "navigate_up", "Up"),
        Binding("down", "navigate_down", "Down"),
        Binding("enter", "select", "Select"),
        Binding("escape", "back", "Back"),
    ]

    selected_index: int = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("[bold]SELECT YOUR CHARACTER[/bold]", id="select-title"),
            Vertical(
                id="character-list",
            ),
            Static("", id="character-preview"),
            id="char-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Populate character list."""
        char_list = self.query_one("#character-list", Vertical)
        # Clear existing children properly
        for child in list(char_list.children):
            child.remove()
        
        for i, (char_id, char_info) in enumerate(CHARACTER_DATA.items()):
            btn = Button(
                f"{char_info.name} - {char_info.title}",
                id=f"char-{char_id}",
                variant="default" if i != self.selected_index else "primary"
            )
            char_list.mount(btn)
        
        self._update_preview()

    def _update_preview(self) -> None:
        """Update character preview panel."""
        chars = list(CHARACTER_DATA.items())
        if chars:
            char_id, char_info = chars[self.selected_index]
            skills_text = "\n".join([f"  {slot.key}: {slot.skill_id}" for slot in char_info.skills])
            preview = f"""[bold]{char_info.name}[/bold]
[i]{char_info.title}[/i]

[b]{char_info.description}[/b]

Skills:
{skills_text}

Press ENTER to select"""
            try:
                self.query_one("#character-preview", Static).update(preview)
            except Exception:
                pass

    def action_navigate_up(self) -> None:
        chars = list(CHARACTER_DATA.keys())
        if chars:
            self.selected_index = (self.selected_index - 1) % len(chars)
            self._update_buttons()
            self._update_preview()

    def action_navigate_down(self) -> None:
        chars = list(CHARACTER_DATA.keys())
        if chars:
            self.selected_index = (self.selected_index + 1) % len(chars)
            self._update_buttons()
            self._update_preview()

    def _update_buttons(self) -> None:
        """Update button variants based on selection."""
        chars = list(CHARACTER_DATA.keys())
        for i, char_id in enumerate(chars):
            try:
                btn = self.query_one(f"#char-{char_id}", Button)
                btn.variant = "primary" if i == self.selected_index else "default"
            except Exception:
                pass

    def action_select(self) -> None:
        """Select current character and start game."""
        chars = list(CHARACTER_DATA.keys())
        if chars:
            selected_char = chars[self.selected_index]
            self.app.selected_character = selected_char
            self.app.pop_screen()  # Pop character select
            self.app.push_screen("game_screen")  # Push game screen

    def action_back(self) -> None:
        self.app.pop_screen()


class GameScreen(Screen):
    """Main game screen with arena and HUD."""

    BINDINGS = [
        Binding("up", "move_up", "Up"),
        Binding("down", "move_down", "Down"),
        Binding("left", "move_left", "Left"),
        Binding("right", "move_right", "Right"),
        Binding("space", "wait", "Wait"),
        Binding("q", "use_skill_q", "Skill Q"),
        Binding("w", "use_skill_w", "Skill W"),
        Binding("e", "use_skill_e", "Skill E"),
        Binding("r", "use_skill_r", "Skill R"),
        Binding("escape", "pause", "Pause"),
    ]

    game: Optional[Game] = None

    def __init__(self, character_id: str = "executioner"):
        super().__init__()
        self.character_id = character_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Container(
            # Arena view
            Static("", id="arena-view"),
            # HUD
            Vertical(
                Horizontal(
                    Static("HP: --/--", id="hp-bar"),
                    Static("EN: --/--", id="energy-bar"),
                    id="stats-row",
                ),
                Horizontal(
                    Static("Q: ---", id="skill-q"),
                    Static("W: ---", id="skill-w"),
                    Static("E: ---", id="skill-e"),
                    Static("R: ---", id="skill-r"),
                    id="skills-row",
                ),
                Static("Wave: -- | Enemies: --", id="wave-info"),
                Static("", id="combat-log"),
                id="hud",
            ),
            id="game-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize game when screen is mounted."""
        # Get selected character from instance or app
        character_id = self.character_id or getattr(self.app, 'selected_character', 'executioner')
        
        # Create game instance
        config = GameConfig(
            screen_width=80,
            screen_height=24,
            arena_width=ARENA_WIDTH,
            arena_height=ARENA_HEIGHT,
        )
        self.game = Game(config)
        self.game.new_game(character_id, "Player")
        
        self._update_display()

    def _update_display(self) -> None:
        """Update the display with current game state."""
        if not self.game:
            return
        
        # Render arena
        try:
            rendered = self.game.render_system.render()
            arena_widget = self.query_one("#arena-view", Static)
            if arena_widget:
                arena_widget.update(str(rendered))
        except Exception as e:
            arena_widget = self.query_one("#arena-view", Static)
            if arena_widget:
                arena_widget.update(f"Error: {e}")
        
        # Update HUD
        try:
            player_data = self.game.player_data
            player_entity = self.game.get_player_entity()
            
            # Get HP and Energy from entity components
            if player_entity:
                from src.components import Health, Energy
                health = self.game.em.get_component(player_entity, Health)
                energy = self.game.em.get_component(player_entity, Energy)
                
                if health:
                    hp = health.current
                    max_hp = health.maximum
                else:
                    hp, max_hp = 50, 50
                    
                if energy:
                    en = energy.current
                    max_en = energy.maximum
                else:
                    en, max_en = 30, 30
            else:
                hp, max_hp = 50, 50
                en, max_en = 30, 30
            
            hp_widget = self.query_one("#hp-bar", Static)
            if hp_widget:
                hp_widget.update(f"HP: {hp}/{max_hp}")
                
            en_widget = self.query_one("#energy-bar", Static)
            if en_widget:
                en_widget.update(f"EN: {en}/{max_en}")
            
            # Update skills from character data
            char_info = CHARACTER_DATA.get(player_data.character_id)
            if char_info:
                skill_map = {slot.key.lower(): slot.skill_id for slot in char_info.skills}
                for key in ['q', 'w', 'e', 'r']:
                    skill_id = skill_map.get(key, '---')
                    widget_id = f"skill-{key}"
                    try:
                        skill_widget = self.query_one(f"#{widget_id}", Static)
                        if skill_widget:
                            skill_widget.update(f"{key.upper()}: {skill_id}")
                    except Exception:
                        pass
            
            # Wave info
            wave = self.game.wave_director.state.current_wave
            remaining = len([e for e in self.game.em.entities if self.game.em.has_component(e, 'ai')])
            wave_widget = self.query_one("#wave-info", Static)
            if wave_widget:
                wave_widget.update(f"Wave: {wave} | Enemies: {remaining}")
        except Exception as e:
            pass

    def action_move_up(self) -> None:
        if self.game:
            self.game.handle_input("up")
            self.call_later(self._sync_process_turn_and_update)

    def action_move_down(self) -> None:
        if self.game:
            self.game.handle_input("down")
            self.call_later(self._sync_process_turn_and_update)

    def action_move_left(self) -> None:
        if self.game:
            self.game.handle_input("left")
            self.call_later(self._sync_process_turn_and_update)

    def action_move_right(self) -> None:
        if self.game:
            self.game.handle_input("right")
            self.call_later(self._sync_process_turn_and_update)

    def action_wait(self) -> None:
        if self.game:
            self.game.handle_input("wait")
            self.call_later(self._sync_process_turn_and_update)

    def _sync_process_turn_and_update(self) -> None:
        """Synchronous wrapper to process turn and update display."""
        if self.game:
            # Use run_async from Textual to properly handle async calls
            async def process():
                await self.game.process_pending_actions()
                self._update_display()
            self.run_worker(process())

    def action_use_skill_q(self) -> None:
        if self.game:
            self.game.handle_input("q")
            self.call_later(self._sync_process_turn_and_update)

    def action_use_skill_w(self) -> None:
        if self.game:
            self.game.handle_input("w")
            self.call_later(self._sync_process_turn_and_update)

    def action_use_skill_e(self) -> None:
        if self.game:
            self.game.handle_input("e")
            self.call_later(self._sync_process_turn_and_update)

    def action_use_skill_r(self) -> None:
        if self.game:
            self.game.handle_input("r")
            self.call_later(self._sync_process_turn_and_update)

    def action_pause(self) -> None:
        self.app.push_screen("pause_menu")


class PauseMenu(Screen):
    """Pause menu screen."""

    BINDINGS = [
        Binding("escape", "resume", "Resume"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("[bold]PAUSED[/bold]", id="pause-title"),
            Vertical(
                Button("RESUME", id="btn-resume"),
                Button("OPTIONS", id="btn-options"),
                Button("QUIT TO MENU", id="btn-quit"),
                id="pause-menu",
            ),
            id="pause-container",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-resume":
            self.app.pop_screen()
        elif event.button.id == "btn-quit":
            self.app.pop_screen()
            self.app.pop_screen()

    def action_resume(self) -> None:
        self.app.pop_screen()


class TurnboundApp(App):
    """Main Textual application for TURNBOUND."""

    selected_character: str = "executioner"

    CSS = """
    Screen {
        background: #0a0a0f;
    }
    
    #main-container {
        align: center middle;
        height: 100%;
        width: 100%;
    }

    #title {
        color: #ff6b6b;
        text-align: center;
        margin-bottom: 1;
        text-style: bold;
    }

    #subtitle {
        text-align: center;
        color: #ff0000;
        margin-bottom: 2;
        text-style: bold;
    }
    
    #decorations {
        text-align: center;
        color: #663399;
        margin-bottom: 1;
    }

    #menu {
        align: center middle;
        width: 30;
        height: auto;
    }
    
    #menu Button {
        width: 100%;
        margin: 1 0;
    }

    #game-container {
        layout: horizontal;
        height: 100%;
        width: 100%;
        padding: 0;
    }

    #arena-view {
        width: 75%;
        height: 100%;
        border: solid #4a4a6a;
        content-align: left top;
        overflow: hidden;
        background: #0d0d15;
    }

    #hud {
        width: 25%;
        height: 100%;
        border: solid #4a4a6a;
        padding: 1;
        background: #0d0d15;
    }

    #stats-row, #skills-row {
        height: auto;
        margin-bottom: 1;
    }

    #hp-bar {
        color: #ff4444;
        width: 50%;
        text-style: bold;
    }

    #energy-bar {
        color: #44aaff;
        width: 50%;
        text-style: bold;
    }
    
    #wave-info {
        color: #aaaaaa;
        margin-top: 1;
        margin-bottom: 1;
    }
    
    #combat-log {
        color: #888888;
        height: 1fr;
    }

    #pause-container {
        align: center middle;
        height: 100%;
    }

    #pause-title {
        text-align: center;
        margin-bottom: 2;
        color: #ffff00;
        text-style: bold;
    }
    
    #pause-menu {
        align: center middle;
        width: 30;
    }
    
    #pause-menu Button {
        width: 100%;
        margin: 1 0;
    }

    #char-container {
        align: center middle;
        height: 100%;
        width: 100%;
    }

    #select-title {
        text-align: center;
        margin-bottom: 2;
        color: #ff6b6b;
        text-style: bold;
    }

    #character-list {
        width: 40;
        height: auto;
        border: solid #4a4a6a;
        padding: 1;
        background: #0d0d15;
    }
    
    #character-list Button {
        width: 100%;
        margin: 1 0;
    }

    #character-preview {
        width: 60;
        height: auto;
        border: solid #663399;
        padding: 1;
        margin-top: 1;
        content-align: left top;
        background: #0d0d15;
    }

    #char-container Vertical {
        align: center middle;
    }
    """

    SCREENS = {
        "title_screen": TitleScreen,
        "game_screen": GameScreen,
        "pause_menu": PauseMenu,
        "character_select": CharacterSelectScreen,
    }

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen("title_screen")


def run_app() -> None:
    """Run the Textual application."""
    app = TurnboundApp()
    app.run()


if __name__ == "__main__":
    run_app()
