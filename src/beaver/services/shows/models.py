from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from beaver.models.base import datamodel
from beaver.services.howlite import models as hlm
from beaver.services.howlite.models import (
    Frequency,
    Query,
    Recurrence,
    RecurrenceRule,
    RecurringQuery,
    TimeRangeQuery,
    Weekday,
    WeekdayRule,
)
from beaver.services.sapphire import enums as spe
from beaver.services.sapphire import models as spm
from beaver.services.sapphire import types as spt

EventType = spe.EventType


@datamodel
class Event:
    """Event data."""

    id: str
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show_id: str
    """Identifier of the show."""

    show: "Show | None"
    """Show the event belongs to."""

    start: datetime
    """Start datetime of the event in event timezone."""

    end: datetime
    """End datetime of the event in event timezone."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence of the event."""

    @classmethod
    def merge(cls, ds: spm.Event, dt: hlm.Event, show: "Show | None") -> "Event":
        """Map to internal representation."""
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

    events: Sequence[Event] | None
    """Events belonging to the show."""

    @staticmethod
    def map(show: spm.Show, events: Sequence[Event] | None) -> "Show":
        """Map to internal representation."""
        return Show(
            id=show.id,
            title=show.title,
            description=show.description,
            events=events,
        )


ShowWhereInput = spt.ShowWhereInput

ShowInclude = spt.ShowInclude

ShowWhereUniqueIdInput = spt._ShowWhereUnique_id_Input  # noqa: SLF001

ShowWhereUniqueTitleInput = spt._ShowWhereUnique_title_Input  # noqa: SLF001

type ShowWhereUniqueInput = ShowWhereUniqueIdInput | ShowWhereUniqueTitleInput

ShowOrderByIdInput = spt._Show_id_OrderByInput  # noqa: SLF001

ShowOrderByTitleInput = spt._Show_title_OrderByInput  # noqa: SLF001

ShowOrderByDescriptionInput = spt._Show_description_OrderByInput  # noqa: SLF001

type ShowOrderByInput = (
    ShowOrderByIdInput | ShowOrderByTitleInput | ShowOrderByDescriptionInput
)

ShowCreateInput = spt.ShowCreateWithoutRelationsInput

ShowUpdateInput = spt.ShowUpdateManyMutationInput


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

    order: ShowOrderByInput | Sequence[ShowOrderByInput] | None
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing shows."""

    shows: Sequence[Show]
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


__all__ = [
    "CountRequest",
    "CountResponse",
    "CreateRequest",
    "CreateResponse",
    "DeleteRequest",
    "DeleteResponse",
    "Event",
    "EventType",
    "Frequency",
    "GetRequest",
    "GetResponse",
    "ListRequest",
    "ListResponse",
    "Query",
    "Recurrence",
    "RecurrenceRule",
    "RecurringQuery",
    "Show",
    "ShowCreateInput",
    "ShowInclude",
    "ShowOrderByDescriptionInput",
    "ShowOrderByIdInput",
    "ShowOrderByInput",
    "ShowOrderByTitleInput",
    "ShowUpdateInput",
    "ShowWhereInput",
    "ShowWhereUniqueIdInput",
    "ShowWhereUniqueInput",
    "ShowWhereUniqueTitleInput",
    "TimeRangeQuery",
    "UpdateRequest",
    "UpdateResponse",
    "Weekday",
    "WeekdayRule",
]
