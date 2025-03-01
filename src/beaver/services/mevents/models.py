from datetime import datetime
from typing import NotRequired, TypedDict
from zoneinfo import ZoneInfo

from beaver.models.base import datamodel
from beaver.services.howlite import models as hlm
from beaver.services.howlite.models import (  # noqa: F401
    Frequency,
    Query,
    Recurrence,
    RecurrenceRule,
    RecurringQuery,
    TimeRangeQuery,
    Weekday,
    WeekdayRule,
)
from beaver.services.sapphire import enums as spe
from beaver.services.sapphire import models as spm
from beaver.services.sapphire import types as spt

EventType = spe.EventType


@datamodel
class Show:
    """Show data."""

    id: str
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: list["Event"] | None
    """Events belonging to the show."""

    @staticmethod
    def map(show: spm.Show, events: list["Event"] | None) -> "Show":
        return Show(
            id=show.id,
            title=show.title,
            description=show.description,
            events=events,
        )


@datamodel
class Event:
    id: str
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show_id: str
    """Identifier of the show."""

    show: Show | None
    """Show the event belongs to."""

    start: datetime
    """Start time of the event in event timezone."""

    end: datetime
    """End time of the event in event timezone."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence of the event."""

    @classmethod
    def merge(cls, ds: spm.Event, dt: hlm.Event, show: Show | None) -> "Event":
        return Event(
            id=ds.id,
            type=ds.type,
            show_id=ds.showId,
            show=show,
            start=dt.start,
            end=dt.end,
            timezone=dt.timezone,
            recurrence=dt.recurrence,
        )


EventWhereInput = spt.EventWhereInput

EventInclude = spt.EventInclude

EventWhereUniqueIdInput = spt._EventWhereUnique_id_Input

EventWhereUniqueInput = EventWhereUniqueIdInput

EventOrderByIdInput = spt._Event_id_OrderByInput

EventOrderByTypeInput = spt._Event_type_OrderByInput

EventOrderByShowIdInput = spt._Event_showId_OrderByInput


class EventOrderByStartInput(TypedDict, total=True):
    """Order by start time."""

    start: spt.SortOrder


class EventOrderByEndInput(TypedDict, total=True):
    """Order by end time."""

    end: spt.SortOrder


class EventOrderByTimezoneInput(TypedDict, total=True):
    """Order by timezone."""

    timezone: spt.SortOrder


EventOrderByInput = (
    EventOrderByIdInput
    | EventOrderByTypeInput
    | EventOrderByShowIdInput
    | EventOrderByStartInput
    | EventOrderByEndInput
    | EventOrderByTimezoneInput
)


class EventCreateInput(spt.EventCreateWithoutRelationsInput):
    start: datetime
    """Start time of the event in event timezone."""

    end: datetime
    """End time of the event in event timezone."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: NotRequired[Recurrence | None]
    """Recurrence of the event."""


class EventUpdateInput(spt.EventUpdateManyMutationInput, total=False):
    start: datetime
    """Start time of the event in event timezone."""

    end: datetime
    """End time of the event in event timezone."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence of the event."""


@datamodel
class CountRequest:
    """Request to count events."""

    where: EventWhereInput | None
    """Filter to apply to find events."""

    query: Query | None
    """Advanced query to apply to find events."""


@datamodel
class CountResponse:
    """Response for counting events."""

    count: int
    """Number of events that match the filter."""


@datamodel
class ListRequest:
    """Request to list events."""

    limit: int | None
    """Maximum number of events to return."""

    offset: int | None
    """Number of events to skip."""

    where: EventWhereInput | None
    """Filter to apply to find events."""

    query: Query | None
    """Advanced query to apply to find events."""

    include: EventInclude | None
    """Relations to include in the response."""

    order: EventOrderByInput | list[EventOrderByInput] | None
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing events."""

    events: list[Event]
    """List of events that match the filter."""


@datamodel
class GetRequest:
    """Request to get a event."""

    where: EventWhereUniqueInput
    """Unique filter to apply to find a event."""

    include: EventInclude | None
    """Relations to include in the response."""


@datamodel
class GetResponse:
    """Response for getting a event."""

    event: Event | None
    """Event that matches the filter."""


@datamodel
class CreateRequest:
    """Request to create a event."""

    data: EventCreateInput
    """Data to create a event."""

    include: EventInclude | None
    """Relations to include in the response."""


@datamodel
class CreateResponse:
    """Response for creating a event."""

    event: Event
    """Created event."""


@datamodel
class UpdateRequest:
    """Request to update a event."""

    data: EventUpdateInput
    """Data to update a event."""

    where: EventWhereUniqueInput
    """Unique filter to apply to find a event."""

    include: EventInclude | None
    """Relations to include in the response."""


@datamodel
class UpdateResponse:
    """Response for updating a event."""

    event: Event | None
    """Event that was updated."""


@datamodel
class DeleteRequest:
    """Request to delete a event."""

    where: EventWhereUniqueInput
    """Unique filter to apply to find a event."""

    include: EventInclude | None
    """Relations to include in the response."""


@datamodel
class DeleteResponse:
    """Response for deleting a event."""

    event: Event | None
    """Event that was deleted."""
