from typing import Annotated

from pydantic import Field, RootModel

from beaver.models.events import mevent as ee
from beaver.models.events import show as se

Event = Annotated[
    ee.EventCreatedEvent
    | ee.EventUpdatedEvent
    | ee.EventDeletedEvent
    | se.ShowCreatedEvent
    | se.ShowUpdatedEvent
    | se.ShowDeletedEvent,
    Field(..., discriminator="type"),
]
ParsableEvent = RootModel[Event]
