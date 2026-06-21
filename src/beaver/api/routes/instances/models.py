from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from typing import Annotated, Self
from uuid import UUID

from pydantic import Field, PositiveInt

from beaver.models.base import SerializableModel, datamodel
from beaver.services.entities.instances import models as im
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


class WeekdayRule(SerializableModel):
    """Day rule data."""

    day: im.Weekday
    """Day of the week."""

    occurrence: Week | None = None
    """Occurrence of the day in the year."""

    @classmethod
    def map(cls, rule: im.WeekdayRule) -> Self:
        """Map from internal representation."""
        return cls(day=rule.day, occurrence=rule.occurrence)


class Recurrence(SerializableModel):
    """Recurrence rule data."""

    frequency: im.Frequency
    """Frequency of the recurrence."""

    until: NaiveDatetime | None = None
    """End datetime of the recurrence in UTC."""

    count: PositiveInt | None = None
    """Number of occurrences of the recurrence."""

    interval: PositiveInt | None = None
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

    by_set_positions: Sequence[Yearday] | None = None
    """Set positions of the recurrence."""

    week_start: im.Weekday | None = None
    """Start day of the week."""

    @classmethod
    def map(cls, rule: im.Recurrence) -> Self:
        """Map from internal representation."""
        return cls(
            frequency=rule.frequency,
            until=rule.until,
            count=rule.count,
            interval=rule.interval,
            by_seconds=rule.by_seconds,
            by_minutes=rule.by_minutes,
            by_hours=rule.by_hours,
            by_weekdays=[WeekdayRule.map(r) for r in rule.by_weekdays]
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
    def map(cls, instance: im.Inclusion) -> Self:
        """Map from internal representation."""
        return cls(start=instance.start)


class Exclusion(SerializableModel):
    """Exclusion data."""

    start: NaiveDatetime
    """Start datetime of the excluded instance in event timezone."""

    @classmethod
    def map(cls, instance: im.Exclusion) -> Self:
        """Map from internal representation."""
        return cls(start=instance.start)


class Show(SerializableModel):
    """Show data."""

    id: UUID
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: Sequence["Event"] | None
    """Events that the show belongs to."""

    @classmethod
    def map(cls, show: im.Show) -> Self:
        """Map from internal representation."""
        return cls(
            id=UUID(show.id),
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

    type: im.EventType
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
    def map(cls, event: im.Event) -> Self:
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


class Instance(SerializableModel):
    """Instance data."""

    start: NaiveDatetime
    """Start datetime of the instance in event timezone."""

    duration: Timedelta
    """Duration of the instance."""

    event_id: UUID
    """Identifier of the event that the instance belongs to."""

    event: Event | None
    """Event that the instance belongs to."""

    @classmethod
    def map(cls, instance: im.Instance) -> Self:
        """Map from internal representation."""
        return cls(
            start=instance.start,
            duration=instance.duration,
            event_id=UUID(instance.event_id),
            event=Event.map(instance.event) if instance.event is not None else None,
        )


class InstanceList(SerializableModel):
    """List of instances."""

    start: NaiveDatetime
    """Start datetime in UTC used to filter instances."""

    end: NaiveDatetime
    """End datetime in UTC used to filter instances."""

    instances: Sequence[Instance]
    """Instances that matched the request."""


class InstanceCreateInput(SerializableModel):
    """Data to create an instance."""

    start: NaiveDatetime
    """Start datetime of the instance in event timezone."""

    event_id: str
    """Identifier of the event that the instance belongs to."""

    def map(self) -> im.InstanceCreateInput:
        """Map to internal representation."""
        return im.InstanceCreateInput(start=self.start, event_id=self.event_id)


type ListRequestStart = NaiveDatetime

type ListRequestEnd = NaiveDatetime

type ListRequestWhere = im.InstanceWhereInput | None

type ListRequestInclude = im.InstanceInclude | None

type ListRequestOrder = (
    im.InstanceOrderByInput | Sequence[im.InstanceOrderByInput] | None
)

type ListResponseResults = InstanceList

type GetRequestEventId = UUID

type GetRequestStart = NaiveDatetime

type GetRequestInclude = im.InstanceInclude | None

type GetResponseInstance = Instance | None

type CreateRequestData = InstanceCreateInput

type CreateRequestInclude = im.InstanceInclude | None

type CreateResponseInstance = Instance

type DeleteRequestEventId = UUID

type DeleteRequestStart = NaiveDatetime


@datamodel
class ListRequest:
    """Request to list instances."""

    start: ListRequestStart
    """Start datetime in UTC to filter instances."""

    end: ListRequestEnd
    """End datetime in UTC to filter instances."""

    where: ListRequestWhere
    """Filter to apply to find instances."""

    include: ListRequestInclude
    """Relations to include in the response."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing instances."""

    results: ListResponseResults
    """List of instances."""


@datamodel
class GetRequest:
    """Request to get an instance."""

    event_id: GetRequestEventId
    """Identifier of the event that the instance to get belongs to."""

    start: GetRequestStart
    """Start datetime of the instance to get in event timezone."""

    include: GetRequestInclude
    """Relations to include in the response."""


@datamodel
class GetResponse:
    """Response for getting an instance."""

    instance: GetResponseInstance
    """Instance that matched the request."""


@datamodel
class CreateRequest:
    """Request to create an instance."""

    data: CreateRequestData
    """Data to create the instance."""

    include: CreateRequestInclude
    """Relations to include in the response."""


@datamodel
class CreateResponse:
    """Response for creating an instance."""

    instance: CreateResponseInstance
    """Instance that was created."""


@datamodel
class DeleteRequest:
    """Request to delete an instance."""

    event_id: DeleteRequestEventId
    """Identifier of the event that the instance to delete belongs to."""

    start: DeleteRequestStart
    """Start datetime of the instance to delete in event timezone."""


@datamodel
class DeleteResponse:
    """Response for deleting an instance."""
