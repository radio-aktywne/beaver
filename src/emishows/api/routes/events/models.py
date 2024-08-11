from typing import Annotated, Literal, NotRequired
from uuid import UUID

from pydantic import Field

from emishows.models.base import SerializableModel, datamodel, serializable
from emishows.services.mevents import models as em
from emishows.utils.time import NaiveDatetime, Timezone

Second = Annotated[int, Field(..., ge=0, le=60)]

Minute = Annotated[int, Field(..., ge=0, le=59)]

Hour = Annotated[int, Field(..., ge=0, le=23)]

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
    """Day rule data."""

    day: em.Weekday
    """Day of the week."""

    occurrence: Week | None = None
    """Occurrence of the day in the year."""

    @staticmethod
    def imap(rule: em.WeekdayRule) -> "WeekdayRule":
        return WeekdayRule(
            day=rule.day,
            occurrence=rule.occurrence,
        )

    def emap(self) -> em.WeekdayRule:
        return em.WeekdayRule(
            day=self.day,
            occurrence=self.occurrence,
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

    by_seconds: list[Second] | None = None
    """Seconds of the recurrence."""

    by_minutes: list[Minute] | None = None
    """Minutes of the recurrence."""

    by_hours: list[Hour] | None = None
    """Hours of the recurrence."""

    by_weekdays: list[WeekdayRule] | None = None
    """Weekdays of the recurrence."""

    by_monthdays: list[Monthday] | None = None
    """Monthdays of the recurrence."""

    by_yeardays: list[Yearday] | None = None
    """Yeardays of the recurrence."""

    by_weeks: list[Week] | None = None
    """Weeks of the recurrence."""

    by_months: list[Month] | None = None
    """Months of the recurrence."""

    by_set_positions: list[int] | None = None
    """Set positions of the recurrence."""

    week_start: em.Weekday | None = None
    """Start day of the week."""

    @staticmethod
    def imap(rule: em.RecurrenceRule) -> "RecurrenceRule":
        return RecurrenceRule(
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

    include: list[NaiveDatetime] | None = None
    """Included dates of the recurrence in event timezone."""

    exclude: list[NaiveDatetime] | None = None
    """Excluded dates of the recurrence in event timezone."""

    @staticmethod
    def imap(recurrence: em.Recurrence) -> "Recurrence":
        return Recurrence(
            rule=(
                RecurrenceRule.imap(recurrence.rule)
                if recurrence.rule is not None
                else None
            ),
            include=recurrence.include,
            exclude=recurrence.exclude,
        )

    def emap(self) -> em.Recurrence:
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

    events: list["Event"] | None
    """Events that the show belongs to."""

    @staticmethod
    def map(show: em.Show) -> "Show":
        return Show(
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
    """Start time of the event in event timezone."""

    end: NaiveDatetime
    """End time of the event in event timezone."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence rule of the event."""

    @staticmethod
    def map(event: em.Event) -> "Event":
        return Event(
            id=event.id,
            type=event.type,
            show_id=event.show_id,
            show=Show.map(event.show) if event.show is not None else None,
            start=event.start,
            end=event.end,
            timezone=str(event.timezone),
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

    events: list[Event]
    """Events that matched the request."""


@serializable
class EventWhereInput(em.EventWhereInput):
    pass


@serializable
@datamodel
class TimeRangeQuery(em.TimeRangeQuery):
    type: Literal["time-range"] = "time-range"

    def map(self) -> em.TimeRangeQuery:
        return em.TimeRangeQuery(
            start=self.start,
            end=self.end,
        )


@serializable
@datamodel
class RecurringQuery(em.RecurringQuery):
    type: Literal["recurring"] = "recurring"

    def map(self) -> em.RecurringQuery:
        return em.RecurringQuery(
            recurring=self.recurring,
        )


Query = Annotated[TimeRangeQuery | RecurringQuery, Field(..., discriminator="type")]


@serializable
class EventWhereUniqueIdInput(em.EventWhereUniqueIdInput):
    pass


EventWhereUniqueInput = EventWhereUniqueIdInput


@serializable
class EventInclude(em.EventInclude):
    pass


@serializable
class EventOrderByIdInput(em.EventOrderByIdInput):
    pass


@serializable
class EventOrderByTypeInput(em.EventOrderByTypeInput):
    pass


@serializable
class EventOrderByShowIdInput(em.EventOrderByShowIdInput):
    pass


EventOrderByInput = (
    EventOrderByIdInput | EventOrderByTypeInput | EventOrderByShowIdInput
)


@serializable
class EventCreateInput(em.EventCreateInput):
    start: NaiveDatetime
    end: NaiveDatetime
    timezone: Timezone
    recurrence: NotRequired[Recurrence | None]


@serializable
class EventUpdateInput(em.EventUpdateInput, total=False):
    start: NaiveDatetime
    end: NaiveDatetime
    timezone: Timezone
    recurrence: Recurrence | None


ListRequestLimit = int | None

ListRequestOffset = int | None

ListRequestWhere = EventWhereInput | None

ListRequestQuery = Query | None

ListRequestInclude = EventInclude | None

ListRequestOrder = EventOrderByInput | list[EventOrderByInput] | None

ListResponseResults = EventList

GetRequestId = UUID

GetRequestInclude = EventInclude | None

GetResponseEvent = Event

CreateRequestData = EventCreateInput

CreateRequestInclude = EventInclude | None

CreateResponseEvent = Event

UpdateRequestData = EventUpdateInput

UpdateRequestId = UUID

UpdateRequestInclude = EventInclude | None

UpdateResponseEvent = Event

DeleteRequestId = UUID


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

    pass
