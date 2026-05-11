"""
TURNBOUND - Main Menu UI
Stylized ASCII menu with animated background and character selection.
"""

import asyncio
import math
import random
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from rich.text import Text
from rich.style import Style
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Footer, Label, Button
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen

if TYPE_CHECKING:
    from src.ui.game_screen import GameScreen

# --- КОНСТАНТЫ СТИЛЯ ---
LOGO_ASCII = r"""
 ████████╗██╗   ██╗██████╗ ███╗   ██╗██████╗  ██████╗ ██╗   ██╗███╗   ██╗██████╗ 
 ╚══██╔══╝██║   ██║██╔══██╗████╗  ██║██╔══██╗██╔═══██╗██║   ██║████╗  ██║██╔══██╗
    ██║   ██║   ██║██████╔╝██╔██╗ ██║██████╔╝██║   ██║██║   ██║██╔██╗ ██║██║  ██║
    ██║   ██║   ██║██╔══██╗██║╚██╗██║██╔══██╗██║   ██║██║   ██║██║╚██╗██║██║  ██║
    ██║   ╚██████╔╝██║  ██║██║ ╚████║██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝
    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝
"""

@dataclass
class Particle:
    x: int
    y: int
    char: str
    speed: float
    color: str

class AnimatedBackground(Static):
    """Виджет анимированного фона (пепел и туман)."""
    
    def on_mount(self) -> None:
        self.particles: List[Particle] = []
        self._width = 80
        self._height = 24
        # Создаем начальные частицы пепла
        for _ in range(30):
            self.particles.append(self._create_particle(random.randint(0, self._height)))
        
        # Таймер обновления фона (~20 FPS для экономии ресурсов)
        self.set_interval(0.05, self.update_particles)

    def _create_particle(self, y: int = 0) -> Particle:
        return Particle(
            x=random.randint(0, 120),
            y=y,
            char=random.choice([".", "'", "·", "✺", "◦"]),
            speed=random.uniform(0.2, 0.8),
            color=random.choice(["#444444", "#662222", "#330033"])
        )

    def update_particles(self) -> None:
        if not self.app.size:
            return
        for p in self.particles:
            p.y += 1 if random.random() < p.speed else 0
            p.x += random.choice([-1, 0, 1]) if random.random() < 0.1 else 0
            
            if p.y >= self.app.size.height:
                p.y = 0
                p.x = random.randint(0, max(1, self.app.size.width - 1))
        
        self.update(self.render_background())

    def render_background(self) -> Text:
        # Генерируем слой тумана с частицами
        lines = []
        height = max(1, self.app.size.height if self.app.size else 24)
        width = max(1, self.app.size.width if self.app.size else 80)
        
        # Создаем сетку
        grid = [[" " for _ in range(width)] for _ in range(height)]
        
        # Рисуем частицы
        for p in self.particles:
            px, py = int(p.x) % width, int(p.y) % height
            if 0 <= py < height and 0 <= px < width:
                grid[py][px] = p.char
        
        # Преобразуем в текст с цветами
        result = Text()
        for row in grid:
            line_text = "".join(row)
            result.append(line_text + "\n", style="dim")
        
        return result


class GlowLogo(Static):
    """Логотип с пульсирующим градиентом."""
    step = reactive(0.0)

    def on_mount(self) -> None:
        self.set_interval(0.05, self.animate)

    def animate(self) -> None:
        self.step += 0.1

    def render(self) -> Text:
        # Вычисляем цвет на основе синусоиды для эффекта пульсации
        red = int(127 + 127 * math.sin(self.step))
        purple = int(127 + 127 * math.sin(self.step + math.pi))
        color = f"rgb({red},0,{purple})"
        
        return Text(LOGO_ASCII, style=Style(color=color, bold=True))


class MenuOption(Static):
    """Интерактивный пункт меню."""
    can_focus = True

    def __init__(self, label: str, option_id: str):
        super().__init__(label, id=option_id)
        self.option_id = option_id
        self.label = label

    def render(self) -> Text:
        if self.has_focus:
            return Text(f"> [ {self.label} ] <", style="bold white on #4e004e")
        return Text(f"  {self.label}  ", style="dim white")

    def on_click(self) -> None:
        app = self.app
        if isinstance(app, TurnboundMenu):
            app.action_select(self.option_id)


class CharacterInfoScreen(Screen):
    """Экран информации о персонажах."""
    
    BINDINGS = [
        Binding("escape,b", "back", "Назад"),
        Binding("up,w", "scroll_up", "Вверх"),
        Binding("down,s", "scroll_down", "Вниз"),
    ]
    
    CHARACTERS = {
        "executioner": {
            "name": "THE EXECUTIONER",
            "desc": "Brutal blood-fueled melee fighter.",
            "mechanic": "Rage: Lower HP = More Power",
            "skills": [
                ("Q", "Cleave", "Wide melee attack"),
                ("W", "Chain Hook", "Pull enemy"),
                ("E", "Blood Surge", "Spend HP for damage"),
                ("R", "Execution", "Instant kill below threshold"),
            ],
            "color": "#aa0000"
        },
        "astromancer": {
            "name": "THE ASTROMANCER",
            "desc": "Temporal and spatial manipulation.",
            "mechanic": "Echo: Abilities repeat after turns",
            "skills": [
                ("Q", "Star Bolt", "Piercing projectile"),
                ("W", "Warp Step", "Teleport"),
                ("E", "Echo Seal", "Repeat previous skill"),
                ("R", "Collapse", "Trigger all echoes"),
            ],
            "color": "#6600aa"
        },
        "plague_saint": {
            "name": "THE PLAGUE SAINT",
            "desc": "Infection and arena corruption.",
            "mechanic": "Infection: Spread disease",
            "skills": [
                ("Q", "Rot Touch", "Poison attack"),
                ("W", "Spore Cloud", "AOE infection field"),
                ("E", "Harvest", "Explode infected enemies"),
                ("R", "Bloom", "Mass mutation/explosion"),
            ],
            "color": "#00aa00"
        },
        "mirror_duelist": {
            "name": "THE MIRROR DUELIST",
            "desc": "Precision, counters, prediction.",
            "mechanic": "Focus: Setup guaranteed crits",
            "skills": [
                ("Q", "Feint", "Guaranteed crit setup"),
                ("W", "Mirror Step", "Dash with illusion"),
                ("E", "Riposte", "Counter stance"),
                ("R", "Perfect Reflection", "Reflect next skill"),
            ],
            "color": "#aaaaaa"
        }
    }
    
    def __init__(self, selected_char: Optional[str] = None):
        super().__init__()
        self.selected_char = selected_char or "executioner"
        self.scroll_offset = 0
    
    def compose(self) -> ComposeResult:
        char_data = self.CHARACTERS.get(self.selected_char, self.CHARACTERS["executioner"])
        
        yield Static(f"[bold {char_data['color']}]{char_data['name']}[/]", id="char-title")
        yield Static(f"[italic]{char_data['desc']}[/]", id="char-desc")
        yield Static(f"[bold]Mechanic:[/] {char_data['mechanic']}", id="char-mechanic")
        
        yield Static("\n[bold]SKILLS:[/]", id="skills-header")
        skills_text = ""
        for key, name, desc in char_data["skills"]:
            skills_text += f"\n  [{char_data['color']}]{key}[/] [bold]{name}[/]: {desc}"
        yield Static(skills_text, id="skills-list")
        
        yield Static("\n[dim]Press ↑↓ to scroll, B/ESC to go back[/]", id="hint")
        yield Footer()
    
    def action_back(self) -> None:
        self.app.pop_screen()
    
    def action_scroll_up(self) -> None:
        self.scroll_offset = max(0, self.scroll_offset - 1)
        # Перерисовка могла бы быть здесь для скроллинга
    
    def action_scroll_down(self) -> None:
        self.scroll_offset += 1


class CharacterSelectScreen(Screen):
    """Экран выбора персонажа перед началом игры."""
    
    BINDINGS = [
        Binding("escape,b", "back", "Назад"),
        Binding("left,a", "prev_char", "Пред."),
        Binding("right,d", "next_char", "След."),
        Binding("enter,space", "start_game", "Старт"),
    ]
    
    CHAR_ORDER = ["executioner", "astromancer", "plague_saint", "mirror_duelist"]
    
    def __init__(self):
        super().__init__()
        self.current_index = 0
    
    @property
    def current_char_id(self) -> str:
        return self.CHAR_ORDER[self.current_index]
    
    def compose(self) -> ComposeResult:
        yield Static("[bold]SELECT YOUR CHAMPION[/]", id="select-title-chars")
        yield self._create_char_display()
        yield Footer()
    
    def _create_char_display(self) -> Static:
        """Создает виджет с информацией о текущем персонаже."""
        char_id = self.current_char_id
        char_data = CharacterInfoScreen.CHARACTERS.get(char_id, CharacterInfoScreen.CHARACTERS["executioner"])
        
        # Индикатор выбора
        indicators = "  ".join([
            f"[{'bold ' + (char_data['color'] if i == self.current_index else 'dim')}]{CharacterInfoScreen.CHARACTERS[c]['name'].split()[1]}[/]"
            for i, c in enumerate(self.CHAR_ORDER)
        ])
        
        content = f"""[bold {char_data['color']}]{char_data['name']}[/]
[italic]{char_data['desc']}[/]
[bold]Mechanic:[/] {char_data['mechanic']}

{indicators}

[dim]← → to change | ENTER to start | ESC to go back[/]"""
        
        return Static(content, id="char-display-chars")
    
    def action_prev_char(self) -> None:
        self.current_index = (self.current_index - 1) % len(self.CHAR_ORDER)
        self._refresh_display()
    
    def action_next_char(self) -> None:
        self.current_index = (self.current_index + 1) % len(self.CHAR_ORDER)
        self._refresh_display()
    
    def action_start_game(self) -> None:
        # Запуск игры с выбранным персонажем
        from src.ui.game_screen import GameScreen
        game_screen = GameScreen(character_id=self.current_char_id)
        self.app.push_screen(game_screen)
    
    def action_back(self) -> None:
        self.app.pop_screen()
    
    def _refresh_display(self) -> None:
        """Обновляет отображение при смене персонажа."""
        # Находим виджет с информацией и обновляем его содержимое
        display_widget = self.query_one("#char-display-chars", Static)
        if display_widget:
            display_widget.update(self._create_char_display().render())


class BestiaryScreen(Screen):
    """Экран бестиария (заглушка)."""
    
    BINDINGS = [
        Binding("escape,b", "back", "Назад"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Static("[bold]BESTIARY[/]", id="bestiary-title")
        yield Static("\nComing soon...\n\nEnemies, elites, and bosses will appear here.", id="bestiary-content")
        yield Static("\n[dim]Press ESC to go back[/]", id="bestiary-hint")
        yield Footer()
    
    def action_back(self) -> None:
        self.app.pop_screen()


class TurnboundMenu(App):
    """Главное приложение TURNBOUND."""
    
    CSS = """
    Screen {
        background: black;
        align: center middle;
    }

    #main-container {
        width: 60;
        height: auto;
        align: center middle;
        padding: 1 2;
    }

    #menu-list {
        margin-top: 1;
        width: auto;
        align: center middle;
    }

    MenuOption {
        width: 40;
        content-align: center middle;
        margin: 1 0;
        height: 1;
    }

    #version {
        color: #662222;
        margin-top: 1;
        text-align: center;
    }
    
    /* Character Info Screen */
    #char-title {
        width: 100%;
        content-align: center top;
        margin-bottom: 1;
    }
    
    #char-desc, #char-mechanic, #skills-header, #skills-list {
        width: 90%;
        content-align: left top;
        margin: 0 2;
    }
    
    /* Character Select Screen */
    #select-title-chars {
        width: 100%;
        content-align: center top;
        margin-bottom: 1;
    }
    
    #char-display-chars {
        width: 90%;
        content-align: left top;
        margin: 0 2;
    }
    
    /* Bestiary Screen */
    #bestiary-title {
        width: 100%;
        content-align: center top;
        margin-bottom: 1;
    }
    
    #bestiary-content {
        width: 80%;
        content-align: center middle;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("up,w", "focus_previous", "Вверх"),
        Binding("down,s", "focus_next", "Вниз"),
        Binding("enter,space", "select", "Выбрать"),
        Binding("escape,q", "quit_app", "Выход"),
    ]

    def compose(self) -> ComposeResult:
        yield AnimatedBackground(id="bg")
        with Vertical(id="main-container"):
            yield GlowLogo()
            yield Static("v 0.1 'Arcane Awakening' MVP", id="version")
            with Vertical(id="menu-list"):
                yield MenuOption("НОВАЯ ИГРА", "start")
                yield MenuOption("ПЕРСОНАЖИ", "chars")
                yield MenuOption("БЕСТИАРИЙ", "bestiary")
                yield MenuOption("ВЫХОД", "exit")
        yield Footer()

    def action_select(self, option_id: Optional[str] = None) -> None:
        target = option_id or (self.focused.id if self.focused else None)
        
        if target == "exit":
            self.exit()
        elif target == "chars":
            self.push_screen(CharacterInfoScreen())
        elif target == "bestiary":
            self.push_screen(BestiaryScreen())
        elif target == "start":
            self.push_screen(CharacterSelectScreen())
        else:
            self.notify(f"Запуск модуля: {target}", severity="information")

    def action_quit_app(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = TurnboundMenu()
    app.run()
