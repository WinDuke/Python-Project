"""Textual UI for TURNBOUND."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Header, Footer, Static, Button, Label
from textual.binding import Binding
from textual.screen import Screen


class TitleScreen(Screen):
    """Main title screen with animated ASCII art."""

    BINDINGS = [
        Binding("enter", "start_game", "Start Game"),
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
            self.app.push_screen("game_screen")
        elif event.button.id == "btn-exit":
            self.app.exit()

    def action_start_game(self) -> None:
        self.app.push_screen("game_screen")

    def action_quit(self) -> None:
        self.app.exit()


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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Container(
            # Arena view
            Static("", id="arena-view"),
            # HUD
            Vertical(
                Horizontal(
                    Static("HP: 50/50", id="hp-bar"),
                    Static("EN: 30/30", id="energy-bar"),
                    id="stats-row",
                ),
                Horizontal(
                    Static("Q: Fireball", id="skill-q"),
                    Static("W: Dash", id="skill-w"),
                    Static("E: Nova", id="skill-e"),
                    Static("R: Blink", id="skill-r"),
                    id="skills-row",
                ),
                Static("Wave: 1 | Enemies: 0", id="wave-info"),
                Static("", id="combat-log"),
                id="hud",
            ),
            id="game-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize game when screen is mounted."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the display with current game state."""
        # This will be connected to the game engine
        pass

    def action_move_up(self) -> None:
        self.app.notify("Move Up")

    def action_move_down(self) -> None:
        self.app.notify("Move Down")

    def action_move_left(self) -> None:
        self.app.notify("Move Left")

    def action_move_right(self) -> None:
        self.app.notify("Move Right")

    def action_wait(self) -> None:
        self.app.notify("Wait")

    def action_use_skill_q(self) -> None:
        self.app.notify("Skill Q")

    def action_use_skill_w(self) -> None:
        self.app.notify("Skill W")

    def action_use_skill_e(self) -> None:
        self.app.notify("Skill E")

    def action_use_skill_r(self) -> None:
        self.app.notify("Skill R")

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

    CSS = """
    #main-container {
        align: center middle;
        height: 100%;
    }

    #title {
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }

    #subtitle {
        text-align: center;
        color: $error;
        margin-bottom: 2;
    }

    #menu {
        align: center middle;
        width: 30;
    }

    #game-container {
        layout: horizontal;
        height: 100%;
    }

    #arena-view {
        width: 80%;
        height: 100%;
        border: solid $primary;
    }

    #hud {
        width: 20%;
        height: 100%;
        border: solid $secondary;
        padding: 1;
    }

    #stats-row, #skills-row {
        height: auto;
        margin-bottom: 1;
    }

    #hp-bar {
        color: $error;
        width: 50%;
    }

    #energy-bar {
        color: $warning;
        width: 50%;
    }

    #pause-container {
        align: center middle;
        height: 100%;
    }

    #pause-title {
        text-align: center;
        margin-bottom: 2;
    }
    """

    SCREENS = {
        "title_screen": TitleScreen,
        "game_screen": GameScreen,
        "pause_menu": PauseMenu,
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
