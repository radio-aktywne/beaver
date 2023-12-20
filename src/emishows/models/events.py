from datetime import datetime
from typing import Annotated, Literal, TypeVar

from pydantic import Field, RootModel

from emishows.events import models as em
from emishows.models.base import SerializableModel
from emishows.shows import models as sm
from emishows.time import utcnow

TypeType = TypeVar("TypeType")
DataType = TypeVar("DataType", bound=SerializableModel)

TypeFieldType = Annotated[
    TypeType,
    Field(description="Type of the event."),
]
CreatedAtFieldType = Annotated[
    datetime,
    Field(default_factory=utcnow, description="Time at which the event was created."),
]
DataFieldType = Annotated[
    DataType,
    Field(description="Data of the event."),
]


class ShowCreatedEventData(SerializableModel):
    """Data of a show created event."""

    show: sm.Show = Field(
        ...,
        title="ShowCreatedEventData.Show",
        description="Show that was created.",
    )


class ShowCreatedEvent(SerializableModel):
    """Event that is emitted when a show is created."""

    type: TypeFieldType[Literal["show-created"]] = Field(
        "show-created",
        title="ShowCreatedEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="ShowCreatedEvent.CreatedAt",
    )
    data: DataFieldType[ShowCreatedEventData] = Field(
        ...,
        title="ShowCreatedEvent.Data",
    )


class ShowUpdatedEventData(SerializableModel):
    """Data of a show updated event."""

    show: sm.Show = Field(
        ...,
        title="ShowUpdatedEventData.Show",
        description="Show that was updated.",
    )


class ShowUpdatedEvent(SerializableModel):
    """Event that is emitted when a show is updated."""

    type: TypeFieldType[Literal["show-updated"]] = Field(
        "show-updated",
        title="ShowUpdatedEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="ShowUpdatedEvent.CreatedAt",
    )
    data: DataFieldType[ShowUpdatedEventData] = Field(
        ...,
        title="ShowUpdatedEvent.Data",
    )


class ShowDeletedEventData(SerializableModel):
    """Data of a show deleted event."""

    show: sm.Show = Field(
        ...,
        title="ShowDeletedEventData.Show",
        description="Show that was deleted.",
    )


class ShowDeletedEvent(SerializableModel):
    """Event that is emitted when a show is deleted."""

    type: TypeFieldType[Literal["show-deleted"]] = Field(
        "show-deleted",
        title="ShowDeletedEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="ShowDeletedEvent.CreatedAt",
    )
    data: DataFieldType[ShowDeletedEventData] = Field(
        ...,
        title="ShowDeletedEvent.Data",
    )


class EventCreatedEventData(SerializableModel):
    """Data of an event created event."""

    event: em.Event = Field(
        ...,
        title="EventCreatedEventData.Event",
        description="Event that was created.",
    )


class EventCreatedEvent(SerializableModel):
    """Event that is emitted when an event is created."""

    type: TypeFieldType[Literal["event-created"]] = Field(
        "event-created",
        title="EventCreatedEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="EventCreatedEvent.CreatedAt",
    )
    data: DataFieldType[EventCreatedEventData] = Field(
        ...,
        title="EventCreatedEvent.Data",
    )


class EventUpdatedEventData(SerializableModel):
    """Data of an event updated event."""

    event: em.Event = Field(
        ...,
        title="EventUpdatedEventData.Event",
        description="Event that was updated.",
    )


class EventUpdatedEvent(SerializableModel):
    """Event that is emitted when an event is updated."""

    type: TypeFieldType[Literal["event-updated"]] = Field(
        "event-updated",
        title="EventUpdatedEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="EventUpdatedEvent.CreatedAt",
    )
    data: DataFieldType[EventUpdatedEventData] = Field(
        ...,
        title="EventUpdatedEvent.Data",
    )


class EventDeletedEventData(SerializableModel):
    """Data of an event deleted event."""

    event: em.Event = Field(
        ...,
        title="EventDeletedEventData.Event",
        description="Event that was deleted.",
    )


class EventDeletedEvent(SerializableModel):
    """Event that is emitted when an event is deleted."""

    type: TypeFieldType[Literal["event-deleted"]] = Field(
        "event-deleted",
        title="EventDeletedEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="EventDeletedEvent.CreatedAt",
    )
    data: DataFieldType[EventDeletedEventData] = Field(
        ...,
        title="EventDeletedEvent.Data",
    )


Event = Annotated[
    ShowCreatedEvent
    | ShowUpdatedEvent
    | ShowDeletedEvent
    | EventCreatedEvent
    | EventUpdatedEvent
    | EventDeletedEvent,
    Field(..., discriminator="type"),
]
ParsableEvent = RootModel[Event]
