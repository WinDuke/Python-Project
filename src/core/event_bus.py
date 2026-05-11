"""Event bus for decoupled game communication."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class GameEvent:
    """Base event class."""
    event_type: str
    source: int | None = None  # Entity ID
    target: int | None = None
    data: Dict[str, Any] = field(default_factory=dict)


# Event type constants
EVENT_HIT = "hit"
EVENT_CRIT = "crit"
EVENT_KILL = "kill"
EVENT_MOVE = "move"
EVENT_DASH = "dash"
EVENT_STATUS_APPLY = "status_apply"
EVENT_STATUS_REMOVE = "status_remove"
EVENT_LEVELUP = "levelup"
EVENT_WAVE_COMPLETE = "wave_complete"
EVENT_BOSS_PHASE_CHANGE = "boss_phase_change"
EVENT_SKILL_USE = "skill_use"
EVENT_DAMAGE_DEALT = "damage_dealt"
EVENT_DAMAGE_TAKEN = "damage_taken"
EVENT_HEAL = "heal"
EVENT_ENERGY_GAIN = "energy_gain"
EVENT_ENERGY_SPEND = "energy_spend"


class EventBus:
    """Centralized event dispatching system."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[GameEvent], None]]] = defaultdict(list)
        self._event_queue: List[GameEvent] = []

    def subscribe(self, event_type: str, callback: Callable[[GameEvent], None]) -> None:
        """Subscribe a callback to an event type."""
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[GameEvent], None]) -> None:
        """Unsubscribe a callback from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    def emit(self, event: GameEvent) -> None:
        """Emit an event immediately."""
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but don't crash the game
                print(f"Event handler error for {event.event_type}: {e}")

    def queue_event(self, event: GameEvent) -> None:
        """Queue an event for later processing."""
        self._event_queue.append(event)

    def process_queue(self) -> None:
        """Process all queued events."""
        events = self._event_queue.copy()
        self._event_queue.clear()
        for event in events:
            self.emit(event)

    def clear(self) -> None:
        """Clear all subscriptions and queued events."""
        self._subscribers.clear()
        self._event_queue.clear()
