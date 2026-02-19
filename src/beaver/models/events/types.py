from typing import Annotated

from pydantic import Field

from beaver.models.events import events, shows, test

type Event = Annotated[
    test.TestEvent
    | shows.ShowCreatedEvent
    | shows.ShowUpdatedEvent
    | shows.ShowDeletedEvent
    | events.EventCreatedEvent
    | events.EventUpdatedEvent
    | events.EventDeletedEvent,
    Field(discriminator="type"),
]
