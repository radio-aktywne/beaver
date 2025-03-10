from collections.abc import AsyncGenerator

from litestar.channels import ChannelsPlugin

from beaver.models.events.event import Event, ParsableEvent
from beaver.services.events import models as m


class EventsService:
    """Service for events."""

    def __init__(self, channels: ChannelsPlugin) -> None:
        self._channels = channels

    async def _subscribe(self) -> AsyncGenerator[Event]:
        subscription = self._channels.start_subscription("events")

        async with subscription as subscriber:
            async for event in subscriber.iter_events():
                event = ParsableEvent.model_validate_json(event)
                yield event.root

    async def subscribe(self, request: m.SubscribeRequest) -> m.SubscribeResponse:
        """Subscribe to app events."""

        events = self._subscribe()

        return m.SubscribeResponse(
            events=events,
        )
