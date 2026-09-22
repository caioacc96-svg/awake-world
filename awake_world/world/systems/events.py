from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable


class WorldEvent(StrEnum):
    TIME_CHANGED = "TIME_CHANGED"
    SUNSET_STARTED = "SUNSET_STARTED"
    WEATHER_CHANGED = "WEATHER_CHANGED"
    PLAYER_ENTERED_SPACE = "PLAYER_ENTERED_SPACE"
    PLAYER_LEFT_SPACE = "PLAYER_LEFT_SPACE"
    PRESENCE_CHANGED = "PRESENCE_CHANGED"
    MICROEVENT_STARTED = "MICROEVENT_STARTED"
    MICROEVENT_ENDED = "MICROEVENT_ENDED"
    AMBIENT_EVENT = "AMBIENT_EVENT"
    TRANSITION_STARTED = "TRANSITION_STARTED"
    TRANSITION_COMPLETED = "TRANSITION_COMPLETED"
    ACTOR_STATE_CHANGED = "ACTOR_STATE_CHANGED"
    WORLD_LOADED = "WORLD_LOADED"
    WORLD_SAVED = "WORLD_SAVED"


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    kind: WorldEvent
    payload: dict[str, Any] = field(default_factory=dict)


class EventBus:
    """Small synchronous bus with an observability ring buffer."""

    def __init__(self, ring_size: int = 256) -> None:
        self._subscribers: dict[WorldEvent, list[Callable[[EventEnvelope], None]]] = defaultdict(list)
        self.recent: deque[EventEnvelope] = deque(maxlen=ring_size)

    def subscribe(self, kind: WorldEvent, callback: Callable[[EventEnvelope], None]) -> Callable[[], None]:
        self._subscribers[kind].append(callback)
        def unsubscribe() -> None:
            callbacks = self._subscribers.get(kind, [])
            if callback in callbacks:
                callbacks.remove(callback)
        return unsubscribe

    def publish(self, kind: WorldEvent, **payload: Any) -> None:
        event = EventEnvelope(kind, payload)
        self.recent.append(event)
        for callback in tuple(self._subscribers.get(kind, ())):
            callback(event)
