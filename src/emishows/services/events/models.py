from collections.abc import AsyncIterator

from emishows.models.base import datamodel
from emishows.models.events.event import Event


@datamodel
class SubscribeRequest:
    """Request to subscribe."""

    pass


@datamodel
class SubscribeResponse:
    """Response for subscribe."""

    events: AsyncIterator[Event]
    """Stream of events."""
