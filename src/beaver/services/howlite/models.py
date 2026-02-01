from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from beaver.models.base import datamodel
from beaver.services.icalendar.models import (
    Calendar,
    Event,
    Frequency,
    Recurrence,
    RecurrenceRule,
    Weekday,
    WeekdayRule,
)


class Query:
    """Base class for queries."""


@datamodel
class TimeRangeQuery(Query):
    """Time range query data."""

    start: datetime | None = None
    """Beginning of the time range in UTC."""

    end: datetime | None = None
    """End of the time range in UTC."""


@datamodel
class RecurringQuery(Query):
    """Recurring query data."""

    recurring: bool
    """Whether to search for recurring or non-recurring events."""


@datamodel
class GetCalendarRequest:
    """Request to get a calendar."""


@datamodel
class GetCalendarResponse:
    """Response for getting a calendar."""

    calendar: Calendar
    """Calendar data."""


@datamodel
class GetEventRequest:
    """Request to get an event."""

    id: UUID
    """Identifier of the event."""


@datamodel
class GetEventResponse:
    """Response for getting an event."""

    event: Event
    """Event data."""


@datamodel
class QueryEventsRequest:
    """Request to query events."""

    query: Query
    """Query to use."""


@datamodel
class QueryEventsResponse:
    """Response for querying events."""

    events: Sequence[Event]
    """Events data."""


@datamodel
class UpsertEventRequest:
    """Request to upsert an event."""

    event: Event
    """Event data."""


@datamodel
class UpsertEventResponse:
    """Response for upserting an event."""

    event: Event
    """Event data."""


@datamodel
class DeleteEventRequest:
    """Request to delete an event."""

    id: UUID
    """Identifier of the event."""


@datamodel
class DeleteEventResponse:
    """Response for deleting an event."""


__all__ = [
    "Calendar",
    "DeleteEventRequest",
    "DeleteEventResponse",
    "Event",
    "Frequency",
    "GetCalendarRequest",
    "GetCalendarResponse",
    "GetEventRequest",
    "GetEventResponse",
    "Query",
    "QueryEventsRequest",
    "QueryEventsResponse",
    "Recurrence",
    "RecurrenceRule",
    "RecurringQuery",
    "TimeRangeQuery",
    "UpsertEventRequest",
    "UpsertEventResponse",
    "Weekday",
    "WeekdayRule",
]
