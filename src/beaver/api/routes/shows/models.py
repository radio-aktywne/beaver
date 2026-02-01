from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from pydantic import Field

from beaver.models.base import SerializableModel, datamodel
from beaver.services.shows import models as sm
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

    day: sm.Weekday
    """Day of the week."""

    occurrence: Week | None = None
    """Occurrence of the day in the year."""

    @staticmethod
    def map(rule: sm.WeekdayRule) -> "WeekdayRule":
        """Map to internal representation."""
        return WeekdayRule(
            day=rule.day,
            occurrence=rule.occurrence,
        )


class RecurrenceRule(SerializableModel):
    """Recurrence rule data."""

    frequency: sm.Frequency
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

    week_start: sm.Weekday | None = None
    """Start day of the week."""

    @staticmethod
    def map(rule: sm.RecurrenceRule) -> "RecurrenceRule":
        """Map to internal representation."""
        return RecurrenceRule(
            frequency=rule.frequency,
            until=rule.until,
            count=rule.count,
            interval=rule.interval,
            by_seconds=rule.by_seconds,
            by_minutes=rule.by_minutes,
            by_hours=rule.by_hours,
            by_weekdays=(
                [WeekdayRule.map(r) for r in rule.by_weekdays]
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


class Recurrence(SerializableModel):
    """Recurrence data."""

    rule: RecurrenceRule | None = None
    """Rule of the recurrence."""

    include: Sequence[NaiveDatetime] | None = None
    """Included datetimes of the recurrence in event timezone."""

    exclude: Sequence[NaiveDatetime] | None = None
    """Excluded datetimes of the recurrence in event timezone."""

    @staticmethod
    def map(recurrence: sm.Recurrence) -> "Recurrence":
        """Map to internal representation."""
        return Recurrence(
            rule=(
                RecurrenceRule.map(recurrence.rule)
                if recurrence.rule is not None
                else None
            ),
            include=recurrence.include,
            exclude=recurrence.exclude,
        )


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

    end: NaiveDatetime
    """End datetime of the event in event timezone."""

    timezone: Timezone
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence rule of the event."""

    @staticmethod
    def map(event: sm.Event) -> "Event":
        """Map to internal representation."""
        return Event(
            id=UUID(event.id),
            type=event.type,
            show_id=UUID(event.show_id),
            show=Show.map(event.show) if event.show is not None else None,
            start=event.start,
            end=event.end,
            timezone=event.timezone,
            recurrence=(
                Recurrence.map(event.recurrence)
                if event.recurrence is not None
                else None
            ),
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

    @staticmethod
    def map(show: sm.Show) -> "Show":
        """Map to internal representation."""
        return Show(
            id=UUID(show.id),
            title=show.title,
            description=show.description,
            events=(
                [Event.map(event) for event in show.events]
                if show.events is not None
                else None
            ),
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


ShowWhereInput = sm.ShowWhereInput

ShowInclude = sm.ShowInclude

ShowOrderByIdInput = sm.ShowOrderByIdInput

ShowOrderByTitleInput = sm.ShowOrderByTitleInput

ShowOrderByDescriptionInput = sm.ShowOrderByDescriptionInput

type ShowOrderByInput = (
    ShowOrderByIdInput | ShowOrderByTitleInput | ShowOrderByDescriptionInput
)

ShowCreateInput = sm.ShowCreateInput

ShowUpdateInput = sm.ShowUpdateInput

type ListRequestLimit = int | None

type ListRequestOffset = int | None

type ListRequestWhere = ShowWhereInput | None

type ListRequestInclude = ShowInclude | None

type ListRequestOrder = ShowOrderByInput | Sequence[ShowOrderByInput] | None

type ListResponseResults = ShowList

type GetRequestId = UUID

type GetRequestInclude = ShowInclude | None

type GetResponseShow = Show

type CreateRequestData = ShowCreateInput

type CreateRequestInclude = ShowInclude | None

type CreateResponseShow = Show

type UpdateRequestData = ShowUpdateInput

type UpdateRequestId = UUID

type UpdateRequestInclude = ShowInclude | None

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
