from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import Field, PositiveInt

from beaver.models.base import SerializableModel, datamodel
from beaver.services.entities.shows import models as sm
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
    def map(cls, termination: sm.CountTermination) -> Self:
        """Map from internal representation."""
        return cls(count=termination.count)


class UntilTermination(SerializableModel):
    """Until termination data."""

    type: Literal["until"] = "until"
    """Type of the termination."""

    until: NaiveDatetime
    """End datetime of the recurrence in UTC."""

    @classmethod
    def map(cls, termination: sm.UntilTermination) -> Self:
        """Map from internal representation."""
        return cls(until=termination.until)


type Termination = Annotated[
    CountTermination | UntilTermination, Field(discriminator="type")
]


class WeekdayRule(SerializableModel):
    """Day rule data."""

    day: sm.Weekday
    """Day of the week."""

    occurrence: Week | None = None
    """Occurrence of the day in the year."""

    @classmethod
    def map(cls, rule: sm.WeekdayRule) -> Self:
        """Map from internal representation."""
        return cls(day=rule.day, occurrence=rule.occurrence)


class Recurrence(SerializableModel):
    """Recurrence rule data."""

    frequency: sm.Frequency
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

    week_start: sm.Weekday | None = None
    """Start day of the week."""

    @classmethod
    def map(cls, rule: sm.Recurrence) -> Self:
        """Map from internal representation."""
        return cls(
            frequency=rule.frequency,
            termination=None
            if rule.termination is None
            else CountTermination.map(rule.termination)
            if rule.termination.type == "count"
            else UntilTermination.map(rule.termination),
            interval=rule.interval,
            by_seconds=rule.by_seconds,
            by_minutes=rule.by_minutes,
            by_hours=rule.by_hours,
            by_weekdays={WeekdayRule.map(r) for r in rule.by_weekdays}  # pyright: ignore[reportUnhashable]
            if rule.by_weekdays is not None
            else None,
            by_monthdays=rule.by_monthdays,
            by_yeardays=rule.by_yeardays,
            by_weeks=rule.by_weeks,
            by_months=rule.by_months,
            by_set_positions=rule.by_set_positions,
            week_start=rule.week_start,
        )


class Inclusion(SerializableModel):
    """Inclusion data."""

    start: NaiveDatetime
    """Start datetime of the included instance in event timezone."""

    @classmethod
    def map(cls, instance: sm.Inclusion) -> Self:
        """Map from internal representation."""
        return cls(start=instance.start)


class Exclusion(SerializableModel):
    """Exclusion data."""

    start: NaiveDatetime
    """Start datetime of the excluded instance in event timezone."""

    @classmethod
    def map(cls, instance: sm.Exclusion) -> Self:
        """Map from internal representation."""
        return cls(start=instance.start)


class Event(SerializableModel):
    """Event data."""

    id: UUID
    """Identifier of the event."""

    type: sm.EventType
    """Type of the event."""

    show_id: UUID
    """Identifier of the show that the event belongs to."""

    show: "Show | None"
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
    def map(cls, event: sm.Event) -> Self:
        """Map from internal representation."""
        return cls(
            id=UUID(event.id),
            type=event.type,
            show_id=UUID(event.show_id),
            show=Show.map(event.show) if event.show is not None else None,
            start=event.start,
            duration=event.duration,
            timezone=event.timezone,
            recurrence=Recurrence.map(event.recurrence)
            if event.recurrence is not None
            else None,
            include={Inclusion.map(i) for i in event.include}  # pyright: ignore[reportUnhashable]
            if event.include is not None
            else None,
            exclude={Exclusion.map(e) for e in event.exclude}  # pyright: ignore[reportUnhashable]
            if event.exclude is not None
            else None,
        )


class Show(SerializableModel):
    """Show data."""

    id: UUID
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: Sequence[Event] | None
    """Events that the show belongs to."""

    @classmethod
    def map(cls, show: sm.Show) -> Self:
        """Map from internal representation."""
        return cls(
            id=UUID(show.id),
            title=show.title,
            description=show.description,
            events=[Event.map(event) for event in show.events]
            if show.events is not None
            else None,
        )


class ShowList(SerializableModel):
    """List of shows."""

    count: int
    """Total number of shows that matched the query."""

    limit: int | None
    """Maximum number of returned shows."""

    offset: int | None
    """Number of shows skipped."""

    shows: Sequence[Show]
    """Shows that matched the request."""


type ListRequestLimit = int | None

type ListRequestOffset = int | None

type ListRequestWhere = sm.ShowWhereInput | None

type ListRequestInclude = sm.ShowInclude | None

type ListRequestOrder = sm.ShowOrderByInput | Sequence[sm.ShowOrderByInput] | None

type ListResponseResults = ShowList

type GetRequestId = UUID

type GetRequestInclude = sm.ShowInclude | None

type GetResponseShow = Show

type CreateRequestData = sm.ShowCreateInput

type CreateRequestInclude = sm.ShowInclude | None

type CreateResponseShow = Show

type UpdateRequestData = sm.ShowUpdateInput

type UpdateRequestId = UUID

type UpdateRequestInclude = sm.ShowInclude | None

type UpdateResponseShow = Show

type DeleteRequestId = UUID


@datamodel
class ListRequest:
    """Request to list shows."""

    limit: ListRequestLimit
    """Maximum number of shows to return."""

    offset: ListRequestOffset
    """Number of shows to skip."""

    where: ListRequestWhere
    """Filter to apply to find shows."""

    include: ListRequestInclude
    """Relations to include in the response."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing shows."""

    results: ListResponseResults
    """List of shows."""


@datamodel
class GetRequest:
    """Request to get a show."""

    id: GetRequestId
    """Identifier of the show to get."""

    include: GetRequestInclude
    """Relations to include in the response."""


@datamodel
class GetResponse:
    """Response for getting a show."""

    show: GetResponseShow
    """Show that matched the request."""


@datamodel
class CreateRequest:
    """Request to create a show."""

    data: CreateRequestData
    """Data to create a show."""

    include: CreateRequestInclude
    """Relations to include in the response."""


@datamodel
class CreateResponse:
    """Response for creating a show."""

    show: CreateResponseShow
    """Show that was created."""


@datamodel
class UpdateRequest:
    """Request to update a show."""

    data: UpdateRequestData
    """Data to update a show."""

    id: UpdateRequestId
    """Identifier of the show to update."""

    include: UpdateRequestInclude
    """Relations to include in the response."""


@datamodel
class UpdateResponse:
    """Response for updating a show."""

    show: UpdateResponseShow
    """Show that was updated."""


@datamodel
class DeleteRequest:
    """Request to delete a show."""

    id: DeleteRequestId
    """Identifier of the show to delete."""


@datamodel
class DeleteResponse:
    """Response for deleting a show."""
