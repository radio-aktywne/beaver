from typing import Annotated
from uuid import UUID

from pydantic import Field

from emishows.models.base import SerializableModel, datamodel, serializable
from emishows.services.icalendar import models as im
from emishows.services.mevents import models as em
from emishows.utils.time import NaiveDatetime, Timezone

Second = Annotated[int, Field(..., ge=0, le=60)]

Minute = Annotated[int, Field(..., ge=0, le=59)]

Hour = Annotated[int, Field(..., ge=0, le=23)]

Monthday = (
    Annotated[int, Field(..., ge=-31, le=-1)] | Annotated[int, Field(..., ge=1, le=31)]
)

Yearday = (
    Annotated[int, Field(..., ge=-366, le=-1)]
    | Annotated[int, Field(..., ge=1, le=366)]
)

Week = (
    Annotated[int, Field(..., ge=-53, le=-1)] | Annotated[int, Field(..., ge=1, le=53)]
)

Month = Annotated[int, Field(..., ge=1, le=12)]


class WeekdayRule(SerializableModel):
    """Day rule data."""

    day: em.Weekday
    """Day of the week."""

    occurrence: Week | None = None
    """Occurrence of the day in the year."""

    @staticmethod
    def map(rule: em.WeekdayRule) -> "WeekdayRule":
        return WeekdayRule(
            day=rule.day,
            occurrence=rule.occurrence,
        )


class RecurrenceRule(SerializableModel):
    """Recurrence rule data."""

    frequency: em.Frequency
    """Frequency of the recurrence."""

    until: NaiveDatetime | None = None
    """End date of the recurrence in UTC."""

    count: int | None = None
    """Number of occurrences of the recurrence."""

    interval: int | None = None
    """Interval of the recurrence."""

    by_seconds: list[Second] | None = None
    """Seconds of the recurrence."""

    by_minutes: list[Minute] | None = None
    """Minutes of the recurrence."""

    by_hours: list[Hour] | None = None
    """Hours of the recurrence."""

    by_weekdays: list[WeekdayRule] | None = None
    """Weekdays of the recurrence."""

    by_monthdays: list[Monthday] | None = None
    """Monthdays of the recurrence."""

    by_yeardays: list[Yearday] | None = None
    """Yeardays of the recurrence."""

    by_weeks: list[Week] | None = None
    """Weeks of the recurrence."""

    by_months: list[Month] | None = None
    """Months of the recurrence."""

    by_set_positions: list[int] | None = None
    """Set positions of the recurrence."""

    week_start: em.Weekday | None = None
    """Start day of the week."""

    @staticmethod
    def map(rule: em.RecurrenceRule) -> "RecurrenceRule":
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

    include: list[NaiveDatetime] | None = None
    """Included dates of the recurrence in event timezone."""

    exclude: list[NaiveDatetime] | None = None
    """Excluded dates of the recurrence in event timezone."""

    @staticmethod
    def map(recurrence: em.Recurrence) -> "Recurrence":
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

    id: str
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: list["Event"] | None
    """Events that the show belongs to."""

    @staticmethod
    def map(show: em.Show) -> "Show":
        return Show(
            id=show.id,
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
    """Start time of the event in event timezone."""

    end: NaiveDatetime
    """End time of the event in event timezone."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence rule of the event."""

    @staticmethod
    def map(event: em.Event) -> "Event":
        return Event(
            id=event.id,
            type=event.type,
            show_id=event.show_id,
            show=Show.map(event.show) if event.show is not None else None,
            start=event.start,
            end=event.end,
            timezone=str(event.timezone),
            recurrence=(
                Recurrence.map(event.recurrence)
                if event.recurrence is not None
                else None
            ),
        )


@serializable
class EventWhereInput(em.EventWhereInput):
    pass


@serializable
class EventInclude(em.EventInclude):
    pass


@serializable
class EventOrderByIdInput(em.EventOrderByIdInput):
    pass


@serializable
class EventOrderByTypeInput(em.EventOrderByTypeInput):
    pass


@serializable
class EventOrderByShowIdInput(em.EventOrderByShowIdInput):
    pass


EventOrderByInput = (
    EventOrderByIdInput | EventOrderByTypeInput | EventOrderByShowIdInput
)


@serializable
@datamodel
class EventInstance(im.EventInstance):
    @staticmethod
    def map(instance: im.EventInstance) -> "EventInstance":
        return EventInstance(**vars(instance))


class Schedule(SerializableModel):
    """Schedule data."""

    event: Event
    """Event data."""

    instances: list[im.EventInstance]
    """Event instances."""


class ScheduleList(SerializableModel):
    """List of event schedules."""

    count: int
    """Total number of schedules that matched the query."""

    limit: int | None
    """Maximum number of returned schedules."""

    offset: int | None
    """Number of schedules skipped."""

    schedules: list[Schedule]
    """Schedules that matched the request."""


ListRequestStart = NaiveDatetime | None

ListRequestEnd = NaiveDatetime | None

ListRequestLimit = int | None

ListRequestOffset = int | None

ListRequestWhere = EventWhereInput | None

ListRequestInclude = EventInclude | None

ListRequestOrder = EventOrderByInput | list[EventOrderByInput] | None

ListResponseResults = ScheduleList


@datamodel
class ListRequest:
    """Request to list schedules."""

    start: ListRequestStart
    """Start time in UTC to filter events instances."""

    end: ListRequestEnd
    """End time in UTC to filter events instances."""

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
