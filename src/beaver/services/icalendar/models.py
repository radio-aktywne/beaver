from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from beaver.models.base import datamodel


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
class CountTermination:
    """Count termination data."""

    type: Literal["count"] = "count"
    """Type of the termination."""

    count: int
    """Number of instances of recurring event."""


@datamodel
class UntilTermination:
    """Until termination data."""

    type: Literal["until"] = "until"
    """Type of the termination."""

    until: datetime
    """End datetime of the recurrence in UTC."""


type Termination = CountTermination | UntilTermination


@datamodel
class WeekdayRule:
    """Day rule data."""

    day: Weekday
    """Day of the week."""

    occurrence: int | None = None
    """Occurrence of the day in the year."""


@datamodel
class Recurrence:
    """Recurrence rule data."""

    frequency: Frequency
    """Frequency of the recurrence."""

    termination: Termination | None = None
    """Termination of the recurrence."""

    interval: int | None = None
    """Interval of the recurrence."""

    by_seconds: AbstractSet[int] | None = None
    """Seconds of the recurrence."""

    by_minutes: AbstractSet[int] | None = None
    """Minutes of the recurrence."""

    by_hours: AbstractSet[int] | None = None
    """Hours of the recurrence."""

    by_weekdays: AbstractSet[WeekdayRule] | None = None
    """Weekdays of the recurrence."""

    by_monthdays: AbstractSet[int] | None = None
    """Monthdays of the recurrence."""

    by_yeardays: AbstractSet[int] | None = None
    """Yeardays of the recurrence."""

    by_weeks: AbstractSet[int] | None = None
    """Weeks of the recurrence."""

    by_months: AbstractSet[int] | None = None
    """Months of the recurrence."""

    by_set_positions: AbstractSet[int] | None = None
    """Set positions of the recurrence."""

    week_start: Weekday | None = None
    """Start day of the week."""


@datamodel
class Inclusion:
    """Inclusion data."""

    start: datetime
    """Start datetime of the included instance in event timezone."""


@datamodel
class Exclusion:
    """Exclusion data."""

    start: datetime
    """Start datetime of the excluded instance in event timezone."""


@datamodel
class Event:
    """Event data."""

    id: UUID
    """Identifier of the event."""

    start: datetime
    """Start datetime of the event in event timezone."""

    duration: timedelta
    """Duration of the event."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: Recurrence | None = None
    """Recurrence rule of the event."""

    include: AbstractSet[Inclusion] | None = None
    """Included instances of the event."""

    exclude: AbstractSet[Exclusion] | None = None
    """Excluded instances of the event."""


@datamodel
class Instance:
    """Instance data."""

    start: datetime
    """Start datetime of the instance in event timezone."""

    duration: timedelta
    """Duration of the instance."""


@datamodel
class Calendar:
    """Calendar date."""

    events: Sequence[Event]
    """Events of the calendar."""
