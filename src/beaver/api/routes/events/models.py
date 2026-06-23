from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from typing import Annotated, Literal, NotRequired, Self, TypedDict
from uuid import UUID

from pydantic import Field, PositiveInt

from beaver.models.base import SerializableModel, datamodel
from beaver.services.entities.events import models as em
from beaver.utils.time import NaiveDatetime, Timedelta, Timezone

type Second = Annotated[int, Field(ge=0, le=59)]

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


class CountTermination(SerializableModel):
    """Count termination data."""

    type: Literal["count"] = "count"
    """Type of the termination."""

    count: PositiveInt
    """Number of instances of recurring event."""

    @classmethod
    def imap(cls, termination: em.CountTermination) -> Self:
        """Map from internal representation."""
        return cls(count=termination.count)

    def emap(self) -> em.CountTermination:
        """Map to internal representation."""
        return em.CountTermination(count=self.count)


class UntilTermination(SerializableModel):
    """Until termination data."""

    type: Literal["until"] = "until"
    """Type of the termination."""

    until: NaiveDatetime
    """End datetime of the recurrence in UTC."""

    @classmethod
    def imap(cls, termination: em.UntilTermination) -> Self:
        """Map from internal representation."""
        return cls(until=termination.until)

    def emap(self) -> em.UntilTermination:
        """Map to internal representation."""
        return em.UntilTermination(until=self.until)


type Termination = Annotated[
    CountTermination | UntilTermination, Field(discriminator="type")
]


class WeekdayRule(SerializableModel):
    """Day rule data."""

    day: em.Weekday
    """Day of the week."""

    occurrence: Week | None = None
    """Occurrence of the day in the year."""

    @classmethod
    def imap(cls, rule: em.WeekdayRule) -> Self:
        """Map from internal representation."""
        return cls(day=rule.day, occurrence=rule.occurrence)

    def emap(self) -> em.WeekdayRule:
        """Map to internal representation."""
        return em.WeekdayRule(day=self.day, occurrence=self.occurrence)


class Recurrence(SerializableModel):
    """Recurrence rule data."""

    frequency: em.Frequency
    """Frequency of the recurrence."""

    termination: Termination | None = None
    """Termination of the recurrence."""

    interval: PositiveInt | None = None
    """Interval of the recurrence."""

    by_seconds: AbstractSet[Second] | None = None
    """Seconds of the recurrence."""

    by_minutes: AbstractSet[Minute] | None = None
    """Minutes of the recurrence."""

    by_hours: AbstractSet[Hour] | None = None
    """Hours of the recurrence."""

    by_weekdays: AbstractSet[WeekdayRule] | None = None
    """Weekdays of the recurrence."""

    by_monthdays: AbstractSet[Monthday] | None = None
    """Monthdays of the recurrence."""

    by_yeardays: AbstractSet[Yearday] | None = None
    """Yeardays of the recurrence."""

    by_weeks: AbstractSet[Week] | None = None
    """Weeks of the recurrence."""

    by_months: AbstractSet[Month] | None = None
    """Months of the recurrence."""

    by_set_positions: AbstractSet[Yearday] | None = None
    """Set positions of the recurrence."""

    week_start: em.Weekday | None = None
    """Start day of the week."""

    @classmethod
    def imap(cls, rule: em.Recurrence) -> Self:
        """Map from internal representation."""
        return cls(
            frequency=rule.frequency,
            termination=None
            if rule.termination is None
            else CountTermination.imap(rule.termination)
            if rule.termination.type == "count"
            else UntilTermination.imap(rule.termination),
            interval=rule.interval,
            by_seconds=rule.by_seconds,
            by_minutes=rule.by_minutes,
            by_hours=rule.by_hours,
            by_weekdays={WeekdayRule.imap(r) for r in rule.by_weekdays}  # pyright: ignore[reportUnhashable]
            if rule.by_weekdays is not None
            else None,
            by_monthdays=rule.by_monthdays,
            by_yeardays=rule.by_yeardays,
            by_weeks=rule.by_weeks,
            by_months=rule.by_months,
            by_set_positions=rule.by_set_positions,
            week_start=rule.week_start,
        )

    def emap(self) -> em.Recurrence:
        """Map to internal representation."""
        return em.Recurrence(
            frequency=self.frequency,
            termination=None
            if self.termination is None
            else CountTermination.emap(self.termination)
            if self.termination.type == "count"
            else UntilTermination.emap(self.termination),
            interval=self.interval,
            by_seconds=self.by_seconds,
            by_minutes=self.by_minutes,
            by_hours=self.by_hours,
            by_weekdays={r.emap() for r in self.by_weekdays}
            if self.by_weekdays is not None
            else None,
            by_monthdays=self.by_monthdays,
            by_yeardays=self.by_yeardays,
            by_weeks=self.by_weeks,
            by_months=self.by_months,
            by_set_positions=self.by_set_positions,
            week_start=self.week_start,
        )


class Inclusion(SerializableModel):
    """Inclusion data."""

    start: NaiveDatetime
    """Start datetime of the included instance in event timezone."""

    @classmethod
    def imap(cls, instance: em.Inclusion) -> Self:
        """Map from internal representation."""
        return cls(start=instance.start)

    def emap(self) -> em.Inclusion:
        """Map to internal representation."""
        return em.Inclusion(start=self.start)


class Exclusion(SerializableModel):
    """Exclusion data."""

    start: NaiveDatetime
    """Start datetime of the excluded instance in event timezone."""

    @classmethod
    def imap(cls, instance: em.Exclusion) -> Self:
        """Map from internal representation."""
        return cls(start=instance.start)

    def emap(self) -> em.Exclusion:
        """Map to internal representation."""
        return em.Exclusion(start=self.start)


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
        """Map from internal representation."""
        return cls(
            id=show.id,
            title=show.title,
            description=show.description,
            events=[Event.map(event) for event in show.events]
            if show.events is not None
            else None,
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

    duration: Timedelta
    """Duration of the event."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: Recurrence | None = None
    """Recurrence rule of the event."""

    include: AbstractSet[Inclusion] | None = None
    """Included instances of the event."""

    exclude: AbstractSet[Exclusion] | None = None
    """Excluded instances of the event."""

    @classmethod
    def map(cls, event: em.Event) -> Self:
        """Map from internal representation."""
        return cls(
            id=UUID(event.id),
            type=event.type,
            show_id=UUID(event.show_id),
            show=Show.map(event.show) if event.show is not None else None,
            start=event.start,
            duration=event.duration,
            timezone=event.timezone,
            recurrence=Recurrence.imap(event.recurrence)
            if event.recurrence is not None
            else None,
            include={Inclusion.imap(i) for i in event.include}  # pyright: ignore[reportUnhashable]
            if event.include is not None
            else None,
            exclude={Exclusion.imap(e) for e in event.exclude}  # pyright: ignore[reportUnhashable]
            if event.exclude is not None
            else None,
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


class EventCreateInput(em.EventCreateInput):
    """Data to create an event."""

    start: NaiveDatetime
    """Start datetime of the event in event timezone."""

    duration: Timedelta
    """Duration of the event."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: NotRequired[Recurrence | None]  # pyright: ignore[reportIncompatibleVariableOverride]
    """Recurrence rule of the event."""

    include: NotRequired[AbstractSet[Inclusion] | None]  # pyright: ignore[reportIncompatibleVariableOverride]
    """Included instances of the event."""

    exclude: NotRequired[AbstractSet[Exclusion] | None]  # pyright: ignore[reportIncompatibleVariableOverride]
    """Excluded instances of the event."""


class RecurrenceUpdateInput(TypedDict, total=False):
    """Data to update a recurrence rule."""

    frequency: em.Frequency
    """Frequency of the recurrence."""

    termination: Termination | None
    """Termination of the recurrence."""

    interval: PositiveInt | None
    """Interval of the recurrence."""

    by_seconds: AbstractSet[Second] | None
    """Seconds of the recurrence."""

    by_minutes: AbstractSet[Minute] | None
    """Minutes of the recurrence."""

    by_hours: AbstractSet[Hour] | None
    """Hours of the recurrence."""

    by_weekdays: AbstractSet[WeekdayRule] | None
    """Weekdays of the recurrence."""

    by_monthdays: AbstractSet[Monthday] | None
    """Monthdays of the recurrence."""

    by_yeardays: AbstractSet[Yearday] | None
    """Yeardays of the recurrence."""

    by_weeks: AbstractSet[Week] | None
    """Weeks of the recurrence."""

    by_months: AbstractSet[Month] | None
    """Months of the recurrence."""

    by_set_positions: AbstractSet[Yearday] | None
    """Set positions of the recurrence."""

    week_start: em.Weekday | None
    """Start day of the week."""


class EventUpdateInput(em.EventUpdateInput, total=False):
    """Data to update an event."""

    start: NaiveDatetime
    """Start datetime of the event in event timezone."""

    duration: Timedelta
    """Duration of the event."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: RecurrenceUpdateInput | None  # pyright: ignore[reportIncompatibleVariableOverride]
    """Recurrence rule of the event."""

    include: AbstractSet[Inclusion] | None  # pyright: ignore[reportIncompatibleVariableOverride]
    """Included instances of the event."""

    exclude: AbstractSet[Exclusion] | None  # pyright: ignore[reportIncompatibleVariableOverride]
    """Excluded instances of the event."""


type ListRequestLimit = int | None

type ListRequestOffset = int | None

type ListRequestWhere = em.EventWhereInput | None

type ListRequestQuery = Query | None

type ListRequestInclude = em.EventInclude | None

type ListRequestOrder = em.EventOrderByInput | Sequence[em.EventOrderByInput] | None

type ListResponseResults = EventList

type GetRequestId = UUID

type GetRequestInclude = em.EventInclude | None

type GetResponseEvent = Event

type CreateRequestData = EventCreateInput

type CreateRequestInclude = em.EventInclude | None

type CreateResponseEvent = Event

type UpdateRequestData = EventUpdateInput

type UpdateRequestId = UUID

type UpdateRequestInclude = em.EventInclude | None

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
