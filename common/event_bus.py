from typing import Callable, Dict, List, Any
from threading import Lock


class EventBus:
    """Simple in-memory event bus implementing Observer pattern."""
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = {}
        self._lock = Lock()

    def subscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        with self._lock:
            self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, payload: Any) -> None:
        # In a real microservice world, this would be a message broker.
        handlers = self._subscribers.get(event_type, [])
        for h in handlers:
            h(payload)


# Global singleton bus for demo (each service could have its own client).
event_bus = EventBus()
