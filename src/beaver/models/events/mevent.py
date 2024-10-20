from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field

from beaver.models.base import SerializableModel
from beaver.models.events import types as t
from beaver.services.mevents import models as em
from beaver.services.shows import models as sm
from beaver.utils.time import NaiveDatetime, Timezone

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


class Event(SerializableModel):
    """Event data."""

    id: str
    """Identifier of the event."""

    type: em.EventType
    """Type of the event."""

    show_id: UUID
    """Identifier of the show the event belongs to."""

    start: NaiveDatetime
    """Start time of the event in event timezone."""

    end: NaiveDatetime
    """End time of the event in event timezone."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: Recurrence | None = None
    """Recurrence of the event."""

    @staticmethod
    def map(event: em.Event | sm.Event) -> "Event":
        return Event(
            id=event.id,
            type=event.type,
            show_id=event.show_id,
            start=event.start,
            end=event.end,
            timezone=str(event.timezone),
            recurrence=(
                Recurrence.map(event.recurrence)
                if event.recurrence is not None
                else None
            ),
        )


class EventCreatedEventData(SerializableModel):
    """Data of a event created event."""

    event: Event
    """Event that was created."""


class EventCreatedEvent(SerializableModel):
    """Event that is emitted when event is created."""

    type: t.TypeFieldType[Literal["event-created"]] = "event-created"
    created_at: t.CreatedAtFieldType
    data: t.DataFieldType[EventCreatedEventData]


class EventUpdatedEventData(SerializableModel):
    """Data of a event updated event."""

    event: Event
    """Event that was updated."""


class EventUpdatedEvent(SerializableModel):
    """Event that is emitted when event is updated."""

    type: t.TypeFieldType[Literal["event-updated"]] = "event-updated"
    created_at: t.CreatedAtFieldType
    data: t.DataFieldType[EventUpdatedEventData]


class EventDeletedEventData(SerializableModel):
    """Data of a event deleted event."""

    event: Event
    """Event that was deleted."""


class EventDeletedEvent(SerializableModel):
    """Event that is emitted when event is deleted."""

    type: t.TypeFieldType[Literal["event-deleted"]] = "event-deleted"
    created_at: t.CreatedAtFieldType
    data: t.DataFieldType[EventDeletedEventData]
