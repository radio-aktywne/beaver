from collections.abc import Sequence
from typing import Annotated, Literal, NotRequired, Self
from uuid import UUID

from pydantic import Field

from beaver.models.base import SerializableModel, datamodel
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

    @classmethod
    def imap(cls, rule: em.WeekdayRule) -> Self:
        """Map to internal representation."""
        return cls(day=rule.day, occurrence=rule.occurrence)

    def emap(self) -> em.WeekdayRule:
        """Map to external representation."""
        return em.WeekdayRule(day=self.day, occurrence=self.occurrence)


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

    @classmethod
    def imap(cls, rule: em.RecurrenceRule) -> Self:
        """Map to internal representation."""
        return cls(
            frequency=rule.frequency,
            until=rule.until,
            count=rule.count,
            interval=rule.interval,
            by_seconds=rule.by_seconds,
            by_minutes=rule.by_minutes,
            by_hours=rule.by_hours,
            by_weekdays=(
                [WeekdayRule.imap(r) for r in rule.by_weekdays]
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

    def emap(self) -> em.RecurrenceRule:
        """Map to external representation."""
        return em.RecurrenceRule(
            frequency=self.frequency,
            until=self.until,
            count=self.count,
            interval=self.interval,
            by_seconds=self.by_seconds,
            by_minutes=self.by_minutes,
            by_hours=self.by_hours,
            by_weekdays=(
                [r.emap() for r in self.by_weekdays]
                if self.by_weekdays is not None
                else None
            ),
            by_monthdays=self.by_monthdays,
            by_yeardays=self.by_yeardays,
            by_weeks=self.by_weeks,
            by_months=self.by_months,
            by_set_positions=self.by_set_positions,
            week_start=self.week_start,
        )


class Recurrence(SerializableModel):
    """Recurrence data."""

    rule: RecurrenceRule | None = None
    """Rule of the recurrence."""

    include: Sequence[NaiveDatetime] | None = None
    """Included datetimes of the recurrence in event timezone."""

    exclude: Sequence[NaiveDatetime] | None = None
    """Excluded datetimes of the recurrence in event timezone."""

    @classmethod
    def imap(cls, recurrence: em.Recurrence) -> Self:
        """Map to internal representation."""
        return cls(
            rule=(
                RecurrenceRule.imap(recurrence.rule)
                if recurrence.rule is not None
                else None
            ),
            include=recurrence.include,
            exclude=recurrence.exclude,
        )

    def emap(self) -> em.Recurrence:
        """Map to external representation."""
        return em.Recurrence(
            rule=(self.rule.emap() if self.rule is not None else None),
            include=self.include,
            exclude=self.exclude,
        )


class Show(SerializableModel):
    """Show data."""

    id: str
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: Sequence["Event"] | None
    """Events that the show belongs to."""

    @classmethod
    def map(cls, show: em.Show) -> Self:
        """Map to internal representation."""
        return cls(
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
    """Start datetime of the event in event timezone."""

    end: NaiveDatetime
    """End datetime of the event in event timezone."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence rule of the event."""

    @classmethod
    def map(cls, event: em.Event) -> Self:
        """Map to internal representation."""
        return cls(
            id=UUID(event.id),
            type=event.type,
            show_id=UUID(event.show_id),
            show=Show.map(event.show) if event.show is not None else None,
            start=event.start,
            end=event.end,
            timezone=event.timezone,
            recurrence=(
                Recurrence.imap(event.recurrence)
                if event.recurrence is not None
                else None
            ),
        )


class EventList(SerializableModel):
    """List of events."""

    count: int
    """Total number of events that matched the query."""

    limit: int | None
    """Maximum number of returned events."""

    offset: int | None
    """Number of events skipped."""

    events: Sequence[Event]
    """Events that matched the request."""


EventWhereInput = em.EventWhereInput


class TimeRangeQuery(SerializableModel):
    """Query for events in a time range."""

    type: Literal["time-range"] = "time-range"
    """Type of the query."""

    start: NaiveDatetime | None = None
    """Beginning of the time range in UTC."""

    end: NaiveDatetime | None = None
    """End of the time range in UTC."""

    def map(self) -> em.TimeRangeQuery:
        """Map to internal representation."""
        return em.TimeRangeQuery(start=self.start, end=self.end)


class RecurringQuery(SerializableModel):
    """Query for recurring events."""

    type: Literal["recurring"] = "recurring"
    """Type of the query."""

    recurring: bool
    """Whether to search for recurring or non-recurring events."""

    def map(self) -> em.RecurringQuery:
        """Map to internal representation."""
        return em.RecurringQuery(recurring=self.recurring)


type Query = Annotated[TimeRangeQuery | RecurringQuery, Field(discriminator="type")]


EventInclude = em.EventInclude


EventOrderByIdInput = em.EventOrderByIdInput


EventOrderByTypeInput = em.EventOrderByTypeInput


EventOrderByShowIdInput = em.EventOrderByShowIdInput


type EventOrderByInput = (
    EventOrderByIdInput | EventOrderByTypeInput | EventOrderByShowIdInput
)


class EventCreateInput(em.EventCreateInput):
    """Input data to create an event."""

    start: NaiveDatetime
    """Start datetime of the event in event timezone."""

    end: NaiveDatetime
    """End datetime of the event in event timezone."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: NotRequired[Recurrence | None]  # pyright: ignore[reportIncompatibleVariableOverride]
    """Recurrence of the event."""


class EventUpdateInput(em.EventUpdateInput, total=False):
    """Input data to update an event."""

    start: NaiveDatetime
    """Start datetime of the event in event timezone."""

    end: NaiveDatetime
    """End datetime of the event in event timezone."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: Recurrence | None  # pyright: ignore[reportIncompatibleVariableOverride]
    """Recurrence of the event."""


type ListRequestLimit = int | None

type ListRequestOffset = int | None

type ListRequestWhere = EventWhereInput | None

type ListRequestQuery = Query | None

type ListRequestInclude = EventInclude | None

type ListRequestOrder = EventOrderByInput | Sequence[EventOrderByInput] | None

type ListResponseResults = EventList

type GetRequestId = UUID

type GetRequestInclude = EventInclude | None

type GetResponseEvent = Event

type CreateRequestData = EventCreateInput

type CreateRequestInclude = EventInclude | None

type CreateResponseEvent = Event

type UpdateRequestData = EventUpdateInput

type UpdateRequestId = UUID

type UpdateRequestInclude = EventInclude | None

type UpdateResponseEvent = Event

type DeleteRequestId = UUID


@datamodel
class ListRequest:
    """Request to list events."""

    limit: ListRequestLimit
    """Maximum number of events to return."""

    offset: ListRequestOffset
    """Number of events to skip."""

    where: ListRequestWhere
    """Filter to apply to find events."""

    query: ListRequestQuery
    """Advanced query to apply to find events."""

    include: ListRequestInclude
    """Relations to include in the response."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing events."""

    results: ListResponseResults
    """List of events."""


@datamodel
class GetRequest:
    """Request to get an event."""

    id: GetRequestId
    """Identifier of the event to get."""

    include: GetRequestInclude
    """Relations to include in the response."""


@datamodel
class GetResponse:
    """Response for getting an event."""

    event: GetResponseEvent
    """Event that matched the request."""


@datamodel
class CreateRequest:
    """Request to create an event."""

    data: CreateRequestData
    """Data to create an event."""

    include: CreateRequestInclude
    """Relations to include in the response."""


@datamodel
class CreateResponse:
    """Response for creating an event."""

    event: CreateResponseEvent
    """Event that was created."""


@datamodel
class UpdateRequest:
    """Request to update an event."""

    data: UpdateRequestData
    """Data to update an event."""

    id: UpdateRequestId
    """Identifier of the event to update."""

    include: UpdateRequestInclude
    """Relations to include in the response."""


@datamodel
class UpdateResponse:
    """Response for updating an event."""

    event: UpdateResponseEvent
    """Event that was updated."""


@datamodel
class DeleteRequest:
    """Request to delete an event."""

    id: DeleteRequestId
    """Identifier of the event to delete."""


@datamodel
class DeleteResponse:
    """Response for deleting an event."""
