from datetime import datetime

from zoneinfo import ZoneInfo

from emishows.models.base import datamodel
from emishows.services.datashows import enums as dse
from emishows.services.datashows import models as dsm
from emishows.services.datashows import types as dst
from emishows.services.datatimes import models as dtm
from emishows.services.datatimes.models import (  # noqa: F401
    Frequency,
    Query,
    Recurrence,
    RecurrenceRule,
    RecurringQuery,
    TimeRangeQuery,
    Weekday,
    WeekdayRule,
)

EventType = dse.EventType


@datamodel
class Event:
    id: str
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show_id: str
    """Identifier of the show."""

    show: "Show | None"
    """Show the event belongs to."""

    start: datetime
    """Start time of the event in event timezone."""

    end: datetime
    """End time of the event in event timezone."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence of the event."""

    @classmethod
    def merge(cls, ds: dsm.Event, dt: dtm.Event, show: "Show | None") -> "Event":
        return Event(
            id=ds.id,
            type=ds.type,
            show_id=ds.showId,
            show=show,
            start=dt.start,
            end=dt.end,
            timezone=dt.timezone,
            recurrence=dt.recurrence,
        )


@datamodel
class Show:
    """Show data."""

    id: str
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: list[Event] | None
    """Events belonging to the show."""

    @staticmethod
    def map(show: dsm.Show, events: list[Event] | None) -> "Show":
        return Show(
            id=show.id,
            title=show.title,
            description=show.description,
            events=events,
        )


ShowWhereInput = dst.ShowWhereInput

ShowInclude = dst.ShowInclude

ShowWhereUniqueIdInput = dst._ShowWhereUnique_id_Input

ShowWhereUniqueTitleInput = dst._ShowWhereUnique_title_Input

ShowWhereUniqueInput = ShowWhereUniqueIdInput | ShowWhereUniqueTitleInput

ShowOrderByIdInput = dst._Show_id_OrderByInput

ShowOrderByTitleInput = dst._Show_title_OrderByInput

ShowOrderByDescriptionInput = dst._Show_description_OrderByInput

ShowOrderByInput = (
    ShowOrderByIdInput | ShowOrderByTitleInput | ShowOrderByDescriptionInput
)

ShowCreateInput = dst.ShowCreateWithoutRelationsInput

ShowUpdateInput = dst.ShowUpdateManyMutationInput


@datamodel
class CountRequest:
    """Request to count shows."""

    where: ShowWhereInput | None
    """Filter to apply to find shows."""


@datamodel
class CountResponse:
    """Response for counting shows."""

    count: int
    """Number of shows that match the filter."""


@datamodel
class ListRequest:
    """Request to list shows."""

    limit: int | None
    """Maximum number of shows to return."""

    offset: int | None
    """Number of shows to skip."""

    where: ShowWhereInput | None
    """Filter to apply to find shows."""

    include: ShowInclude | None
    """Relations to include in the response."""

    order: ShowOrderByInput | list[ShowOrderByInput] | None
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing shows."""

    shows: list[Show]
    """List of shows that match the filter."""


@datamodel
class GetRequest:
    """Request to get a show."""

    where: ShowWhereUniqueInput
    """Unique filter to apply to find a show."""

    include: ShowInclude | None
    """Relations to include in the response."""


@datamodel
class GetResponse:
    """Response for getting a show."""

    show: Show | None
    """Show that matches the filter."""


@datamodel
class CreateRequest:
    """Request to create a show."""

    data: ShowCreateInput
    """Data to create a show."""

    include: ShowInclude | None
    """Relations to include in the response."""


@datamodel
class CreateResponse:
    """Response for creating a show."""

    show: Show
    """Created show."""


@datamodel
class UpdateRequest:
    """Request to update a show."""

    data: ShowUpdateInput
    """Data to update a show."""

    where: ShowWhereUniqueInput
    """Unique filter to apply to find a show."""

    include: ShowInclude | None
    """Relations to include in the response."""


@datamodel
class UpdateResponse:
    """Response for updating a show."""

    show: Show | None
    """Show that was updated."""


@datamodel
class DeleteRequest:
    """Request to delete a show."""

    where: ShowWhereUniqueInput
    """Unique filter to apply to find a show."""

    include: ShowInclude | None
    """Relations to include in the response."""


@datamodel
class DeleteResponse:
    """Response for deleting a show."""

    show: Show | None
    """Show that was deleted."""
