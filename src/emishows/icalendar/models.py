from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, NaiveDatetime

from emishows.models.base import SerializableModel
from emishows.time import Timezone

Frequency = Literal[
    "secondly",
    "minutely",
    "hourly",
    "daily",
    "weekly",
    "monthly",
    "yearly",
]

Second = Annotated[int, Field(..., ge=0, le=60)]

Minute = Annotated[int, Field(..., ge=0, le=59)]

Hour = Annotated[int, Field(..., ge=0, le=23)]

Weekday = Literal[
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

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
    """Day rule model."""

    day: Weekday = Field(
        ...,
        title="DayRule.Day",
        description="Day of the week.",
    )
    occurrence: Week | None = Field(
        None,
        title="DayRule.Occurrence",
        description="Occurrence of the day in the year.",
    )


class RecurrenceRule(SerializableModel):
    """Recurrence rule model."""

    frequency: Frequency = Field(
        ...,
        title="RecurrenceRule.Frequency",
        description="Frequency of the recurrence.",
    )
    until: NaiveDatetime | None = Field(
        None,
        title="RecurrenceRule.Until",
        description="End date of the recurrence in UTC.",
    )
    count: int | None = Field(
        None,
        title="RecurrenceRule.Count",
        description="Number of occurrences of the recurrence.",
    )
    interval: int | None = Field(
        None,
        title="RecurrenceRule.Interval",
        description="Interval of the recurrence.",
    )
    by_seconds: list[Second] | None = Field(
        None,
        title="RecurrenceRule.BySeconds",
        description="Seconds of the recurrence.",
    )
    by_minutes: list[Minute] | None = Field(
        None,
        title="RecurrenceRule.ByMinutes",
        description="Minutes of the recurrence.",
    )
    by_hours: list[Hour] | None = Field(
        None,
        title="RecurrenceRule.ByHours",
        description="Hours of the recurrence.",
    )
    by_weekdays: list[WeekdayRule] | None = Field(
        None,
        title="RecurrenceRule.ByWeekdays",
        description="Weekdays of the recurrence.",
    )
    by_monthdays: list[Monthday] | None = Field(
        None,
        title="RecurrenceRule.ByMonthdays",
        description="Monthdays of the recurrence.",
    )
    by_yeardays: list[Yearday] | None = Field(
        None,
        title="RecurrenceRule.ByYeardays",
        description="Yeardays of the recurrence.",
    )
    by_weeks: list[Week] | None = Field(
        None,
        title="RecurrenceRule.ByWeeks",
        description="Weeks of the recurrence.",
    )
    by_months: list[Month] | None = Field(
        None,
        title="RecurrenceRule.ByMonths",
        description="Months of the recurrence.",
    )
    by_set_positions: list[int] | None = Field(
        None,
        title="RecurrenceRule.BySetPositions",
        description="Set positions of the recurrence.",
    )
    week_start: Weekday | None = Field(
        None,
        title="RecurrenceRule.WeekStart",
        description="Start day of the week.",
    )


class Recurrence(SerializableModel):
    """Recurrence model."""

    rule: RecurrenceRule | None = Field(
        None,
        title="Recurrence.Rule",
        description="Rule of the recurrence.",
    )
    include: list[NaiveDatetime] | None = Field(
        None,
        title="Recurrence.Include",
        description="Included dates of the recurrence in event timezone.",
    )
    exclude: list[NaiveDatetime] | None = Field(
        None,
        title="Recurrence.Exclude",
        description="Excluded dates of the recurrence in event timezone.",
    )


class Event(SerializableModel):
    """Event model."""

    id: UUID = Field(
        ...,
        title="Event.Id",
        description="Identifier of the event.",
    )
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


class Calendar(SerializableModel):
    """Calendar model."""

    events: list[Event] = Field(
        ...,
        title="Calendar.Events",
        description="Events of the calendar.",
    )


class EventInstance(SerializableModel):
    """Event instance."""

    start: NaiveDatetime = Field(
        ...,
        title="EventInstance.Start",
        description="Start time of the event instance in event timezone.",
    )
    end: NaiveDatetime = Field(
        ...,
        title="EventInstance.End",
        description="End time of the event instance in event timezone.",
    )
