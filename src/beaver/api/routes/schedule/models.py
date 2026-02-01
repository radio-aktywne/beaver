from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from pydantic import Field

from beaver.models.base import SerializableModel, datamodel
from beaver.services.icalendar import models as im
from beaver.services.mevents import models as em
from beaver.utils.time import NaiveDatetime, Timezone

type Second = Annotated[int, Field(ge=0, le=60)]

type Minute = Annotated[int, Field(ge=0, le=59)]

type Hour = Annotated[int, Field(ge=0, le=23)]

type Monthday = (
    Annotated[int, Field(ge=-31, le=-1)] | Annotated[int, Field(ge=1, le=31)]
)

type Yearday = (
    Annotated[int, Field(ge=-366, le=-1)] | Annotated[int, Field(ge=1, le=366)]
)

type Week = Annotated[int, Field(ge=-53, le=-1)] | Annotated[int, Field(ge=1, le=53)]

type Month = Annotated[int, Field(ge=1, le=12)]


class WeekdayRule(SerializableModel):
    """Day rule data."""

    day: em.Weekday
    """Day of the week."""

    occurrence: Week | None = None
    """Occurrence of the day in the year."""

    @staticmethod
    def map(rule: em.WeekdayRule) -> "WeekdayRule":
        """Map to internal representation."""
        return WeekdayRule(
            day=rule.day,
            occurrence=rule.occurrence,
        )


class RecurrenceRule(SerializableModel):
    """Recurrence rule data."""

    frequency: em.Frequency
    """Frequency of the recurrence."""

    until: NaiveDatetime | None = None
    """End datetime of the recurrence in UTC."""

    count: int | None = None
    """Number of occurrences of the recurrence."""

    interval: int | None = None
    """Interval of the recurrence."""

    by_seconds: Sequence[Second] | None = None
    """Seconds of the recurrence."""

    by_minutes: Sequence[Minute] | None = None
    """Minutes of the recurrence."""

    by_hours: Sequence[Hour] | None = None
    """Hours of the recurrence."""

    by_weekdays: Sequence[WeekdayRule] | None = None
    """Weekdays of the recurrence."""

    by_monthdays: Sequence[Monthday] | None = None
    """Monthdays of the recurrence."""

    by_yeardays: Sequence[Yearday] | None = None
    """Yeardays of the recurrence."""

    by_weeks: Sequence[Week] | None = None
    """Weeks of the recurrence."""

    by_months: Sequence[Month] | None = None
    """Months of the recurrence."""

    by_set_positions: Sequence[int] | None = None
    """Set positions of the recurrence."""

    week_start: em.Weekday | None = None
    """Start day of the week."""

    @staticmethod
    def map(rule: em.RecurrenceRule) -> "RecurrenceRule":
        """Map to internal representation."""
        return RecurrenceRule(
            frequency=rule.frequency,
            until=rule.until,
            count=rule.count,
            interval=rule.interval,
            by_seconds=rule.by_seconds,
            by_minutes=rule.by_minutes,
            by_hours=rule.by_hours,
            by_weekdays=(
                [WeekdayRule.map(r) for r in rule.by_weekdays]
                if rule.by_weekdays is not None
                else None
            ),
            by_monthdays=rule.by_monthdays,
            by_yeardays=rule.by_yeardays,
            by_weeks=rule.by_weeks,
            by_months=rule.by_months,
            by_set_positions=rule.by_set_positions,
            week_start=rule.week_start,
        )


class Recurrence(SerializableModel):
    """Recurrence data."""

    rule: RecurrenceRule | None = None
    """Rule of the recurrence."""

    include: Sequence[NaiveDatetime] | None = None
    """Included datetimes of the recurrence in event timezone."""

    exclude: Sequence[NaiveDatetime] | None = None
    """Excluded datetimes of the recurrence in event timezone."""

    @staticmethod
    def map(recurrence: em.Recurrence) -> "Recurrence":
        """Map to internal representation."""
        return Recurrence(
            rule=(
                RecurrenceRule.map(recurrence.rule)
                if recurrence.rule is not None
                else None
            ),
            include=recurrence.include,
            exclude=recurrence.exclude,
        )


class Show(SerializableModel):
    """Show data."""

    id: UUID
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: Sequence["Event"] | None
    """Events that the show belongs to."""

    @staticmethod
    def map(show: em.Show) -> "Show":
        """Map to internal representation."""
        return Show(
            id=UUID(show.id),
            title=show.title,
            description=show.description,
            events=(
                [Event.map(event) for event in show.events]
                if show.events is not None
                else None
            ),
        )


class Event(SerializableModel):
    """Event data."""

    id: UUID
    """Identifier of the event."""

    type: em.EventType
    """Type of the event."""

    show_id: UUID
    """Identifier of the show that the event belongs to."""

    show: Show | None
    """Show that the event belongs to."""

    start: NaiveDatetime
    """Start datetime of the event in event timezone."""

    end: NaiveDatetime
    """End datetime of the event in event timezone."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence rule of the event."""

    @staticmethod
    def map(event: em.Event) -> "Event":
        """Map to internal representation."""
        return Event(
            id=UUID(event.id),
            type=event.type,
            show_id=UUID(event.show_id),
            show=Show.map(event.show) if event.show is not None else None,
            start=event.start,
            end=event.end,
            timezone=event.timezone,
            recurrence=(
                Recurrence.map(event.recurrence)
                if event.recurrence is not None
                else None
            ),
        )


EventWhereInput = em.EventWhereInput

EventInclude = em.EventInclude

EventOrderByIdInput = em.EventOrderByIdInput

EventOrderByTypeInput = em.EventOrderByTypeInput

EventOrderByShowIdInput = em.EventOrderByShowIdInput

type EventOrderByInput = (
    EventOrderByIdInput | EventOrderByTypeInput | EventOrderByShowIdInput
)


class EventInstance(SerializableModel):
    """Event instance data."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""

    end: NaiveDatetime
    """End datetime of the event instance in event timezone."""

    @staticmethod
    def map(instance: im.EventInstance) -> "EventInstance":
        """Map to internal representation."""
        return EventInstance(start=instance.start, end=instance.end)


class Schedule(SerializableModel):
    """Schedule data."""

    event: Event
    """Event data."""

    instances: Sequence[EventInstance]
    """Event instances."""


class ScheduleList(SerializableModel):
    """List of event schedules."""

    count: int
    """Total number of schedules that matched the query."""

    limit: int | None
    """Maximum number of returned schedules."""

    offset: int | None
    """Number of schedules skipped."""

    schedules: Sequence[Schedule]
    """Schedules that matched the request."""


type ListRequestStart = NaiveDatetime | None

type ListRequestEnd = NaiveDatetime | None

type ListRequestLimit = int | None

type ListRequestOffset = int | None

type ListRequestWhere = EventWhereInput | None

type ListRequestInclude = EventInclude | None

type ListRequestOrder = EventOrderByInput | Sequence[EventOrderByInput] | None

type ListResponseResults = ScheduleList


@datamodel
class ListRequest:
    """Request to list schedules."""

    start: ListRequestStart
    """Start datetime in UTC to filter events instances."""

    end: ListRequestEnd
    """End datetime in UTC to filter events instances."""

    limit: ListRequestLimit
    """Maximum number of schedules to return."""

    offset: ListRequestOffset
    """Number of schedules to skip."""

    where: ListRequestWhere
    """Filter to apply to find events."""

    include: ListRequestInclude
    """Relations to include in the response."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing schedules."""

    results: ListResponseResults
    """List of schedules."""
