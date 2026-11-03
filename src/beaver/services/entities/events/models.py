from collections.abc import Sequence
from datetime import datetime
from typing import NotRequired, TypedDict

from beaver.models.base import datamodel
from beaver.services.persistence.events import models as pm


EventType = pm.EventType

Frequency = pm.Frequency

Weekday = pm.Weekday

CountTermination = pm.CountTermination

UntilTermination = pm.UntilTermination

type Termination = pm.Termination

WeekdayRule = pm.WeekdayRule

Recurrence = pm.Recurrence

Inclusion = pm.Inclusion

Exclusion = pm.Exclusion

Show = pm.Show

Event = pm.Event

EventWhereInput = pm.EventWhereInput

EventInclude = pm.EventInclude

EventWhereUniqueIdInput = pm.EventWhereUniqueIdInput

type EventWhereUniqueInput = EventWhereUniqueIdInput

Query = pm.Query

RecurringQuery = pm.RecurringQuery

TimeRangeQuery = pm.TimeRangeQuery

EventOrderByIdInput = pm.EventOrderByIdInput

EventOrderByTypeInput = pm.EventOrderByTypeInput

EventOrderByShowIdInput = pm.EventOrderByShowIdInput

type EventOrderByInput = (
    EventOrderByIdInput | EventOrderByTypeInput | EventOrderByShowIdInput
)

EventCreateInput = pm.EventCreateInput

RecurrenceUpdateInput = pm.RecurrenceUpdateInput

EventUpdateInput = pm.EventUpdateInput


class EventSplitInput(TypedDict):
    """Data to split an event."""

    at: datetime
    """Datetime in event timezone of the instance to split the event at."""

    update: NotRequired[EventUpdateInput | None]
    """Data to update the event after the split."""


@datamodel
class SplitResult:
    """Result of splitting an event."""

    before: Event
    """Event before the split."""

    after: Event
    """Event after the split."""


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
    """Event that was created."""


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
class SplitRequest:
    """Request to split an event."""

    data: EventSplitInput
    """Data to split an event."""

    where: EventWhereUniqueInput
    """Unique filter to apply to find an event."""

    include: EventInclude | None
    """Relations to include in the response."""


@datamodel
class SplitResponse:
    """Response for splitting an event."""

    result: SplitResult | None
    """Result of splitting the event."""


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
