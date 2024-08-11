from datetime import datetime
from enum import StrEnum
from uuid import UUID

from zoneinfo import ZoneInfo

from emishows.models.base import datamodel


class Frequency(StrEnum):
    """Frequency options."""

    SECONDLY = "secondly"
    MINUTELY = "minutely"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Weekday(StrEnum):
    """Weekday options."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@datamodel
class WeekdayRule:
    """Day rule data."""

    day: Weekday
    """Day of the week."""

    occurrence: int | None = None
    """Occurrence of the day in the year."""


@datamodel
class RecurrenceRule:
    """Recurrence rule data."""

    frequency: Frequency
    """Frequency of the recurrence."""

    until: datetime | None = None
    """End date of the recurrence in UTC."""

    count: int | None = None
    """Number of occurrences of the recurrence."""

    interval: int | None = None
    """Interval of the recurrence."""

    by_seconds: list[int] | None = None
    """Seconds of the recurrence."""

    by_minutes: list[int] | None = None
    """Minutes of the recurrence."""

    by_hours: list[int] | None = None
    """Hours of the recurrence."""

    by_weekdays: list[WeekdayRule] | None = None
    """Weekdays of the recurrence."""

    by_monthdays: list[int] | None = None
    """Monthdays of the recurrence."""

    by_yeardays: list[int] | None = None
    """Yeardays of the recurrence."""

    by_weeks: list[int] | None = None
    """Weeks of the recurrence."""

    by_months: list[int] | None = None
    """Months of the recurrence."""

    by_set_positions: list[int] | None = None
    """Set positions of the recurrence."""

    week_start: Weekday | None = None
    """Start day of the week."""


@datamodel
class Recurrence:
    """Recurrence data."""

    rule: RecurrenceRule | None = None
    """Rule of the recurrence."""

    include: list[datetime] | None = None
    """Included dates of the recurrence in event timezone."""

    exclude: list[datetime] | None = None
    """Excluded dates of the recurrence in event timezone."""


@datamodel
class Event:
    """Event data."""

    id: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event in event timezone."""

    end: datetime
    """End time of the event in event timezone."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: Recurrence | None = None
    """Recurrence of the event."""


@datamodel
class Calendar:
    """Calendar date."""

    events: list[Event]
    """Events of the calendar."""


@datamodel
class EventInstance:
    """Event instance data."""

    start: datetime
    """Start time of the event instance in event timezone."""

    end: datetime
    """End time of the event instance in event timezone."""
