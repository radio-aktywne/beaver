from datetime import datetime
from uuid import UUID

from emishows.models.base import datamodel
from emishows.services.icalendar.models import (  # noqa: F401
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

    pass


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

    pass


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

    events: list[Event]
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

    pass
