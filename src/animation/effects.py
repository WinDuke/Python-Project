"""Animation system for visual effects."""

from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
import asyncio


@dataclass
class AnimationFrame:
    """A single frame of an animation."""
    x: int
    y: int
    symbol: str
    color: str = "white"
    bg_color: str | None = None
    bold: bool = False
    blink: bool = False
    duration_ms: int = 50


@dataclass
class Animation:
    """Complete animation sequence."""
    id: str
    frames: List[AnimationFrame] = field(default_factory=list)
    total_duration_ms: int = 0
    loop: bool = False
    on_complete: Optional[Callable] = None
    
    def add_frame(
        self,
        x: int,
        y: int,
        symbol: str,
        color: str = "white",
        duration_ms: int = 50,
        bold: bool = False,
    ) -> None:
        """Add a frame to the animation."""
        self.frames.append(AnimationFrame(
            x=x, y=y, symbol=symbol, color=color,
            bold=bold, duration_ms=duration_ms
        ))
        self.total_duration_ms += duration_ms


@dataclass
class Particle:
    """A single particle effect."""
    x: float
    y: float
    vx: float  # Velocity X
    vy: float  # Velocity Y
    symbol: str
    color: str
    life: int  # Frames remaining
    max_life: int
    gravity: float = 0.0
    fade: bool = True  # Fade out over time
    
    def update(self) -> bool:
        """Update particle and return False if dead."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        return self.life > 0
    
    def get_symbol(self) -> str:
        """Get current symbol based on life."""
        if not self.fade:
            return self.symbol
        
        life_ratio = self.life / self.max_life
        if life_ratio > 0.75:
            return self.symbol
        elif life_ratio > 0.5:
            return self.symbol.lower() if self.symbol.isupper() else self.symbol
        elif life_ratio > 0.25:
            return "."
        else:
            return "·"


@dataclass
class ScreenShake:
    """Screen shake effect."""
    intensity: int = 3
    duration_ms: int = 200
    elapsed_ms: int = 0
    offset_x: int = 0
    offset_y: int = 0
    
    def update(self, delta_ms: int) -> bool:
        """Update shake and return False if done."""
        self.elapsed_ms += delta_ms
        if self.elapsed_ms >= self.duration_ms:
            return False
        
        # Random offset based on remaining time
        ratio = 1.0 - (self.elapsed_ms / self.duration_ms)
        import random
        self.offset_x = random.randint(-self.intensity, self.intensity) * int(ratio)
        self.offset_y = random.randint(-self.intensity, self.intensity) * int(ratio)
        return True


class AnimationSystem:
    """Manages all animations and effects."""
    
    def __init__(self):
        self.active_animations: list[Animation] = []
        self.particles: list[Particle] = []
        self.screen_shake: ScreenShake | None = None
        self._running = False
    
    def start_animation(self, animation: Animation) -> None:
        """Start an animation."""
        self.active_animations.append(animation)
    
    def spawn_projectile(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        symbol: str,
        color: str = "yellow",
        duration_ms: int = 150,
    ) -> None:
        """Create a projectile animation."""
        import math
        
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
        
        steps = max(int(distance), 3)
        frame_duration = duration_ms // steps
        
        anim = Animation(id="projectile")
        
        for i in range(steps + 1):
            t = i / steps
            x = int(start_x + dx * t)
            y = int(start_y + dy * t)
            anim.add_frame(x, y, symbol, color, frame_duration, bold=True)
        
        self.start_animation(anim)
    
    def spawn_explosion(
        self,
        center_x: int,
        center_y: int,
        radius: int = 2,
        symbol: str = "✦",
        color: str = "bright_yellow",
        duration_ms: int = 200,
    ) -> None:
        """Create an explosion animation."""
        anim = Animation(id="explosion")
        frame_duration = duration_ms // (radius + 1)
        
        # Expand outward
        for r in range(radius + 1):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) + abs(dy) <= r:
                        x = center_x + dx
                        y = center_y + dy
                        anim.add_frame(x, y, symbol, color, frame_duration, bold=True)
        
        self.start_animation(anim)
        
        # Add particles
        self.spawn_particles(center_x, center_y, count=8, color=color)
    
    def spawn_particles(
        self,
        x: int,
        y: int,
        count: int = 5,
        symbol: str = "*",
        color: str = "yellow",
        spread: float = 3.0,
        life: int = 10,
        gravity: float = 0.1,
    ) -> None:
        """Spawn particle effects."""
        import random
        
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(0.5, spread)
            
            self.particles.append(Particle(
                x=float(x),
                y=float(y),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                symbol=symbol,
                color=color,
                life=life,
                max_life=life,
                gravity=gravity,
            ))
    
    def trigger_screen_shake(
        self,
        intensity: int = 3,
        duration_ms: int = 200,
    ) -> None:
        """Trigger screen shake effect."""
        self.screen_shake = ScreenShake(
            intensity=intensity,
            duration_ms=duration_ms,
        )
    
    def update(self, delta_ms: int = 50) -> None:
        """Update all animations and effects."""
        import math
        
        # Update animations
        completed = []
        for anim in self.active_animations:
            # For simplicity, we consider animations instant in MVP
            # Full implementation would track frame timing
            completed.append(anim)
        
        for anim in completed:
            self.active_animations.remove(anim)
            if anim.on_complete:
                anim.on_complete()
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Update screen shake
        if self.screen_shake:
            if not self.screen_shake.update(delta_ms):
                self.screen_shake = None
    
    def get_render_data(self) -> dict:
        """Get current animation render data."""
        return {
            "animations": self.active_animations,
            "particles": self.particles,
            "shake": self.screen_shake,
        }
    
    def clear(self) -> None:
        """Clear all active effects."""
        self.active_animations.clear()
        self.particles.clear()
        self.screen_shake = None


# ============================================================================
# PREDEFINED ANIMATIONS
# ============================================================================

def create_slash_arc(
    start_x: int,
    start_y: int,
    direction: str,
    length: int = 3,
    color: str = "cyan",
) -> Animation:
    """Create a slash arc animation."""
    anim = Animation(id="slash")
    
    directions = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0),
        "up_left": (-1, -1),
        "up_right": (1, -1),
        "down_left": (-1, 1),
        "down_right": (1, 1),
    }
    
    dx, dy = directions.get(direction, (1, 0))
    symbols = ["/", "-", "\\"]
    
    for i in range(length):
        x = start_x + dx * i
        y = start_y + dy * i
        symbol = symbols[i % len(symbols)]
        anim.add_frame(x, y, symbol, color, 50, bold=True)
    
    return anim


def create_lightning_bolt(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    color: str = "bright_cyan",
) -> Animation:
    """Create a lightning bolt animation."""
    anim = Animation(id="lightning")
    
    import random
    
    dx = end_x - start_x
    dy = end_y - start_y
    steps = max(abs(dx), abs(dy), 3)
    
    x, y = start_x, start_y
    for i in range(steps):
        anim.add_frame(x, y, "⚡", color, 30, bold=True)
        
        # Zigzag
        if random.random() < 0.5:
            x += 1 if dx > 0 else -1 if dx < 0 else random.choice([-1, 1])
        if random.random() < 0.5:
            y += 1 if dy > 0 else -1 if dy < 0 else random.choice([-1, 1])
    
    anim.add_frame(end_x, end_y, "💥", "bright_yellow", 100, bold=True)
    
    return anim


def create_heal_pulse(
    x: int,
    y: int,
    radius: int = 2,
    color: str = "green",
) -> Animation:
    """Create a healing pulse animation."""
    anim = Animation(id="heal")
    
    for r in range(radius + 1):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if abs(dx) + abs(dy) == r:
                    anim.add_frame(
                        x + dx, y + dy,
                        "✦", color,
                        40, bold=True
                    )
    
    return anim


# Import math at module level
import math
