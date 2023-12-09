from typing import Annotated, Literal

from pydantic import Field, NaiveDatetime

from emishows.icalendar import models as im
from emishows.models.base import SerializableModel

Frequency = im.Frequency
Second = im.Second
Minute = im.Minute
Hour = im.Hour
Weekday = im.Weekday
Monthday = im.Monthday
Yearday = im.Yearday
Week = im.Week
Month = im.Month
WeekdayRule = im.WeekdayRule
RecurrenceRule = im.RecurrenceRule
Recurrence = im.Recurrence
Event = im.Event
Calendar = im.Calendar


class TimeRangeQuery(SerializableModel):
    """Time range query model."""

    type: Literal["time-range"] = Field(
        "time-range",
        title="TimeRangeQuery.Type",
        description="Type of the query.",
    )
    start: NaiveDatetime | None = Field(
        None,
        title="TimeRangeQuery.Start",
        description="Beginning of the time range in UTC.",
    )
    end: NaiveDatetime | None = Field(
        None,
        title="TimeRangeQuery.End",
        description="End of the time range in UTC.",
    )


class RecurringQuery(SerializableModel):
    """Recurring query model."""

    type: Literal["recurring"] = Field(
        "recurring",
        title="RecurringQuery.Type",
        description="Type of the query.",
    )
    recurring: bool = Field(
        ...,
        title="RecurringQuery.Recurring",
        description="Whether to search for recurring or non-recurring events.",
    )


Query = Annotated[TimeRangeQuery | RecurringQuery, Field(..., discriminator="type")]
