from collections.abc import Sequence
from datetime import datetime
from typing import NotRequired, Self, TypedDict
from zoneinfo import ZoneInfo

from beaver.models.base import datamodel
from beaver.services.data.howlite import models as hm
from beaver.services.data.sapphire import enums as se
from beaver.services.data.sapphire import models as sm
from beaver.services.data.sapphire import types as st

EventType = se.EventType

Frequency = hm.Frequency

Weekday = hm.Weekday

WeekdayRule = hm.WeekdayRule

RecurrenceRule = hm.RecurrenceRule

Recurrence = hm.Recurrence


@datamodel
class Show:
    """Show data."""

    id: str
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: Sequence["Event"] | None
    """Events belonging to the show."""

    @classmethod
    def map(cls, show: sm.Show, events: Sequence["Event"] | None) -> Self:
        """Map from internal representation."""
        return cls(
            id=show.id, title=show.title, description=show.description, events=events
        )


@datamodel
class Event:
    """Event data."""

    id: str
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show_id: str
    """Identifier of the show."""

    show: Show | None
    """Show the event belongs to."""

    start: datetime
    """Start datetime of the event in event timezone."""

    end: datetime
    """End datetime of the event in event timezone."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence of the event."""

    @classmethod
    def map(cls, ds: sm.Event, dt: hm.Event, show: Show | None) -> "Event":
        """Map from internal representation."""
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


EventWhereInput = st.EventWhereInput

EventInclude = st.EventInclude

EventWhereUniqueIdInput = st._EventWhereUnique_id_Input  # noqa: SLF001

type EventWhereUniqueInput = EventWhereUniqueIdInput

Query = hm.Query

RecurringQuery = hm.RecurringQuery

TimeRangeQuery = hm.TimeRangeQuery

EventOrderByIdInput = st._Event_id_OrderByInput  # noqa: SLF001

EventOrderByTypeInput = st._Event_type_OrderByInput  # noqa: SLF001

EventOrderByShowIdInput = st._Event_showId_OrderByInput  # noqa: SLF001


class EventOrderByStartInput(TypedDict, total=True):
    """Order by start time."""

    start: st.SortOrder


class EventOrderByEndInput(TypedDict, total=True):
    """Order by end time."""

    end: st.SortOrder


class EventOrderByTimezoneInput(TypedDict, total=True):
    """Order by timezone."""

    timezone: st.SortOrder


type EventOrderByInput = (
    EventOrderByIdInput
    | EventOrderByTypeInput
    | EventOrderByShowIdInput
    | EventOrderByStartInput
    | EventOrderByEndInput
    | EventOrderByTimezoneInput
)


class EventCreateInput(st.EventCreateWithoutRelationsInput):
    """Input data to create an event."""

    start: datetime
    """Start datetime of the event in event timezone."""

    end: datetime
    """End datetime of the event in event timezone."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: NotRequired[Recurrence | None]
    """Recurrence of the event."""


class EventUpdateInput(st.EventUpdateManyMutationInput, total=False):
    """Input data to update an event."""

    start: datetime
    """Start datetime of the event in event timezone."""

    end: datetime
    """End datetime of the event in event timezone."""

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

    order: EventOrderByInput | Sequence[EventOrderByInput] | None
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing events."""

    events: Sequence[Event]
    """List of events that match the filter."""


@datamodel
class GetRequest:
    """Request to get an event."""

    where: EventWhereUniqueInput
    """Unique filter to apply to find an event."""

    include: EventInclude | None
    """Relations to include in the response."""


@datamodel
class GetResponse:
    """Response for getting an event."""

    event: Event | None
    """Event that matches the filter."""


@datamodel
class CreateRequest:
    """Request to create an event."""

    data: EventCreateInput
    """Data to create an event."""

    include: EventInclude | None
    """Relations to include in the response."""


@datamodel
class CreateResponse:
    """Response for creating an event."""

    event: Event
    """Created event."""


@datamodel
class UpdateRequest:
    """Request to update an event."""

    data: EventUpdateInput
    """Data to update an event."""

    where: EventWhereUniqueInput
    """Unique filter to apply to find an event."""

    include: EventInclude | None
    """Relations to include in the response."""


@datamodel
class UpdateResponse:
    """Response for updating an event."""

    event: Event | None
    """Event that was updated."""


@datamodel
class DeleteRequest:
    """Request to delete an event."""

    where: EventWhereUniqueInput
    """Unique filter to apply to find an event."""

    include: EventInclude | None
    """Relations to include in the response."""


@datamodel
class DeleteResponse:
    """Response for deleting an event."""

    event: Event | None
    """Event that was deleted."""
