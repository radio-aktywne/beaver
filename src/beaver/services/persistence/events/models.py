from collections.abc import Set as AbstractSet
from datetime import datetime, timedelta
from typing import NotRequired, TypedDict
from zoneinfo import ZoneInfo

from beaver.services.data.howlite import models as hm
from beaver.services.data.sapphire import types as st
from beaver.services.persistence.reader import models as rm


Event = rm.Event

Show = rm.Show

EventType = rm.EventType

Frequency = rm.Frequency

Weekday = rm.Weekday

CountTermination = rm.CountTermination

UntilTermination = rm.UntilTermination

type Termination = rm.Termination

WeekdayRule = rm.WeekdayRule

Recurrence = rm.Recurrence

Inclusion = rm.Inclusion

Exclusion = rm.Exclusion

EventWhereInput = st.EventWhereInput

EventWhereUniqueInput = st.EventWhereUniqueInput

EventWhereUniqueIdInput = st._EventWhereUnique_id_Input  # noqa: SLF001

EventInclude = st.EventInclude

EventOrderByInput = st.EventOrderByInput

EventOrderByIdInput = st._Event_id_OrderByInput  # noqa: SLF001

EventOrderByTypeInput = st._Event_type_OrderByInput  # noqa: SLF001

EventOrderByShowIdInput = st._Event_showId_OrderByInput  # noqa: SLF001

Query = hm.Query

RecurringQuery = hm.RecurringQuery

TimeRangeQuery = hm.TimeRangeQuery


class EventCreateInput(st.EventCreateWithoutRelationsInput):
    """Data to create an event."""

    start: datetime
    """Start datetime of the event in event timezone."""

    duration: timedelta
    """Duration of the event."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: NotRequired[hm.Recurrence | None]
    """Recurrence rule of the event."""

    include: NotRequired[AbstractSet[hm.Inclusion] | None]
    """Included instances of the event."""

    exclude: NotRequired[AbstractSet[hm.Exclusion] | None]
    """Excluded instances of the event."""


class RecurrenceUpdateInput(TypedDict, total=False):
    """Data to update a recurrence rule."""

    frequency: hm.Frequency
    """Frequency of the recurrence."""

    termination: hm.Termination | None
    """Termination of the recurrence."""

    interval: int | None
    """Interval of the recurrence."""

    by_seconds: AbstractSet[int] | None
    """Seconds of the recurrence."""

    by_minutes: AbstractSet[int] | None
    """Minutes of the recurrence."""

    by_hours: AbstractSet[int] | None
    """Hours of the recurrence."""

    by_weekdays: AbstractSet[hm.WeekdayRule] | None
    """Weekdays of the recurrence."""

    by_monthdays: AbstractSet[int] | None
    """Monthdays of the recurrence."""

    by_yeardays: AbstractSet[int] | None
    """Yeardays of the recurrence."""

    by_weeks: AbstractSet[int] | None
    """Weeks of the recurrence."""

    by_months: AbstractSet[int] | None
    """Months of the recurrence."""

    by_set_positions: AbstractSet[int] | None
    """Set positions of the recurrence."""

    week_start: hm.Weekday | None
    """Start day of the week."""


class EventUpdateInput(st.EventUpdateManyMutationInput, total=False):
    """Data to update an event."""

    start: datetime
    """Start datetime of the event in event timezone."""

    duration: timedelta
    """Duration of the event."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: RecurrenceUpdateInput | None
    """Recurrence rule of the event."""

    include: AbstractSet[hm.Inclusion] | None
    """Included instances of the event."""

    exclude: AbstractSet[hm.Exclusion] | None
    """Excluded instances of the event."""
