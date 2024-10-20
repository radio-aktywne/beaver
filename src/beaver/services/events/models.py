from collections.abc import AsyncIterator

from beaver.models.base import datamodel
from beaver.models.events.event import Event


@datamodel
class SubscribeRequest:
    """Request to subscribe."""

    pass


@datamodel
class SubscribeResponse:
    """Response for subscribe."""

    events: AsyncIterator[Event]
    """Stream of events."""
