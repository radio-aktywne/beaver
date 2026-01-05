from collections.abc import Sequence
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field

from beaver.models.base import SerializableModel
from beaver.models.events import types as t
from beaver.services.mevents import models as em
from beaver.services.shows import models as sm
from beaver.utils.time import NaiveDatetime, Timezone, naiveutcnow

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
    """End date of the recurrence in UTC."""

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
    """Included dates of the recurrence in event timezone."""

    exclude: Sequence[NaiveDatetime] | None = None
    """Excluded dates of the recurrence in event timezone."""

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


class Event(SerializableModel):
    """Event data."""

    id: UUID
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
        """Map to internal representation."""
        return Event(
            id=UUID(event.id),
            type=event.type,
            show_id=UUID(event.show_id),
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

    type: t.TypeField[Literal["event-created"]] = "event-created"
    created_at: t.CreatedAtField = Field(default_factory=naiveutcnow)
    data: t.DataField[EventCreatedEventData]


class EventUpdatedEventData(SerializableModel):
    """Data of a event updated event."""

    event: Event
    """Event that was updated."""


class EventUpdatedEvent(SerializableModel):
    """Event that is emitted when event is updated."""

    type: t.TypeField[Literal["event-updated"]] = "event-updated"
    created_at: t.CreatedAtField = Field(default_factory=naiveutcnow)
    data: t.DataField[EventUpdatedEventData]


class EventDeletedEventData(SerializableModel):
    """Data of a event deleted event."""

    event: Event
    """Event that was deleted."""


class EventDeletedEvent(SerializableModel):
    """Event that is emitted when event is deleted."""

    type: t.TypeField[Literal["event-deleted"]] = "event-deleted"
    created_at: t.CreatedAtField = Field(default_factory=naiveutcnow)
    data: t.DataField[EventDeletedEventData]
