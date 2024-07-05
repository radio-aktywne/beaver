from typing import Annotated, NotRequired

from prisma import models as pm
from prisma import types as pt
from pydantic import Field, NaiveDatetime, PlainValidator, TypeAdapter
from typing_extensions import TypedDict

from emishows.datatimes import models as em
from emishows.models.base import SerializableModel
from emishows.time import Timezone

# Monkey-patching to simplify types
pt.ShowOrderByInput = (
    pt._Show_id_OrderByInput
    | pt._Show_title_OrderByInput
    | pt._Show_description_OrderByInput
)
pt.EventOrderByInput = (
    pt._Event_id_OrderByInput
    | pt._Event_type_OrderByInput
    | pt._Event_showId_OrderByInput
)

EventDatashowsModel = pm.Event
Recurrence = em.Recurrence
SortOrder = pt.SortOrder
EventWhereInput = pt.EventWhereInput
TimeRangeQuery = em.TimeRangeQuery
RecurringQuery = em.RecurringQuery
Query = em.Query
EventInclude = pt.EventInclude
EventWhereUniqueInput = pt.EventWhereUniqueInput


class Event(EventDatashowsModel):
    """Event model."""

    start: NaiveDatetime = Field(
        ...,
        title="Event.Start",
        description="Start time of the event in event timezone.",
    )
    end: NaiveDatetime = Field(
        ...,
        title="Event.End",
        description="End time of the event in event timezone.",
    )
    timezone: Timezone = Field(
        ...,
        title="Event.Timezone",
        description="Timezone of the event.",
    )
    recurrence: Recurrence | None = Field(
        None,
        title="Event.Recurrence",
        description="Recurrence of the event.",
    )


class EventStartOrderByInput(TypedDict, total=True):
    """Order by start time."""

    start: SortOrder


class EventEndOrderByInput(TypedDict, total=True):
    """Order by end time."""

    end: SortOrder


class EventTimezoneOrderByInput(TypedDict, total=True):
    """Order by timezone."""

    timezone: SortOrder


EventOrderByInput = (
    pt.EventOrderByInput
    | EventStartOrderByInput
    | EventEndOrderByInput
    | EventTimezoneOrderByInput
)


class EventCreateInput(pt.EventCreateInput):
    """Input to create an event."""

    start: Annotated[
        str,
        PlainValidator(
            lambda value: TypeAdapter(NaiveDatetime)
            .validate_strings(str(value), strict=True)
            .isoformat()
        ),
    ]
    end: Annotated[
        str,
        PlainValidator(
            lambda value: TypeAdapter(NaiveDatetime)
            .validate_strings(str(value), strict=True)
            .isoformat()
        ),
    ]
    timezone: Timezone
    recurrence: NotRequired[Recurrence | None]


class EventUpdateInput(pt.EventUpdateInput, total=False):
    """Input to update an event."""

    start: Annotated[
        str,
        PlainValidator(
            lambda value: TypeAdapter(NaiveDatetime)
            .validate_strings(str(value), strict=True)
            .isoformat()
        ),
    ]
    end: Annotated[
        str,
        PlainValidator(
            lambda value: TypeAdapter(NaiveDatetime)
            .validate_strings(str(value), strict=True)
            .isoformat()
        ),
    ]
    timezone: Timezone
    recurrence: Recurrence | None


class CountRequest(SerializableModel):
    """Request to count events."""

    where: EventWhereInput | None = Field(
        None,
        title="CountRequest.Where",
        description="Filter to apply to events.",
    )
    query: Query | None = Field(
        None,
        title="CountRequest.Query",
        description="Advanced query to apply to events.",
    )


class CountResponse(SerializableModel):
    """Response for counting events."""

    count: int = Field(
        ...,
        title="CountResponse.Count",
        description="Number of events that matched the request.",
    )


class ListRequest(SerializableModel):
    """Request to list events."""

    limit: int | None = Field(
        None,
        title="ListRequest.Limit",
        description="Maximum number of events to return.",
    )
    offset: int | None = Field(
        None,
        title="ListRequest.Offset",
        description="Number of events to skip.",
    )
    where: EventWhereInput | None = Field(
        None,
        title="ListRequest.Where",
        description="Filter to apply to events.",
    )
    query: Query | None = Field(
        None,
        title="ListRequest.Query",
        description="Advanced query to apply to events.",
    )
    include: EventInclude | None = Field(
        None,
        title="ListRequest.Include",
        description="Relations to include with events.",
    )
    order: EventOrderByInput | list[EventOrderByInput] | None = Field(
        None,
        title="ListRequest.Order",
        description="Order to apply to events.",
    )


class ListResponse(SerializableModel):
    """Response for listing events."""

    events: list[Event] = Field(
        ...,
        title="ListResponse.Events",
        description="Events that matched the request.",
    )


class GetRequest(SerializableModel):
    """Request to get an event."""

    where: EventWhereUniqueInput = Field(
        ...,
        title="GetRequest.Where",
        description="Filter to apply to event.",
    )
    include: EventInclude | None = Field(
        None,
        title="GetRequest.Include",
        description="Relations to include with event.",
    )


class GetResponse(SerializableModel):
    """Response for getting an event."""

    event: Event | None = Field(
        ...,
        title="GetResponse.Event",
        description="Event that matched the request.",
    )


class CreateRequest(SerializableModel):
    """Request to create an event."""

    data: EventCreateInput = Field(
        ...,
        title="CreateRequest.Data",
        description="Data to use to create an event.",
    )
    include: EventInclude | None = Field(
        None,
        title="CreateRequest.Include",
        description="Relations to include with event.",
    )


class CreateResponse(SerializableModel):
    """Response for creating an event."""

    event: Event = Field(
        ...,
        title="CreateResponse.Event",
        description="Event that was created.",
    )


class UpdateRequest(SerializableModel):
    """Request to update an event."""

    data: EventUpdateInput = Field(
        ...,
        title="UpdateRequest.Data",
        description="Data to use to update an event.",
    )
    where: EventWhereUniqueInput = Field(
        ...,
        title="UpdateRequest.Where",
        description="Filter to apply to event.",
    )
    include: EventInclude | None = Field(
        None,
        title="UpdateRequest.Include",
        description="Relations to include with event.",
    )


class UpdateResponse(SerializableModel):
    """Response for updating an event."""

    event: Event | None = Field(
        ...,
        title="UpdateResponse.Event",
        description="Event that was updated.",
    )


class DeleteRequest(SerializableModel):
    """Request to delete an event."""

    where: EventWhereUniqueInput = Field(
        ...,
        title="DeleteRequest.Where",
        description="Filter to apply to event.",
    )
    include: EventInclude | None = Field(
        None,
        title="DeleteRequest.Include",
        description="Relations to include with event.",
    )


class DeleteResponse(SerializableModel):
    """Response for deleting an event."""

    event: Event | None = Field(
        ...,
        title="DeleteResponse.Event",
        description="Event that was deleted.",
    )
