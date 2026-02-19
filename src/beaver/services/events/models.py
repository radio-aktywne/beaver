from collections.abc import AsyncIterator
from collections.abc import Set as AbstractSet

from beaver.models.base import datamodel
from beaver.models.events.enums import EventType
from beaver.models.events.types import Event


@datamodel
class SubscribeRequest:
    """Request to subscribe."""

    types: AbstractSet[EventType] | None = None
    """Types of events to subscribe to."""


@datamodel
class SubscribeResponse:
    """Response for subscribe."""

    events: AsyncIterator[Event]
    """Stream of events."""
