from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from datetime import datetime, timedelta
from typing import Self
from zoneinfo import ZoneInfo

from beaver.models.base import datamodel
from beaver.services.data.howlite import models as hm
from beaver.services.data.sapphire import enums as se
from beaver.services.data.sapphire import models as sm
from beaver.services.data.sapphire import types as st

EventType = se.EventType

Frequency = hm.Frequency

Weekday = hm.Weekday

WeekdayRule = hm.WeekdayRule

Recurrence = hm.Recurrence

Inclusion = hm.Inclusion

Exclusion = hm.Exclusion


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

    duration: timedelta
    """Duration of the event."""

    timezone: ZoneInfo
    """Timezone of the event."""

    recurrence: Recurrence | None
    """Recurrence rule of the event."""

    include: AbstractSet[Inclusion] | None
    """Included instances of the event."""

    exclude: AbstractSet[Exclusion] | None
    """Excluded instances of the event."""

    @classmethod
    def map(cls, ds: sm.Event, dt: hm.Event, show: "Show | None") -> "Event":
        """Map from internal representation."""
        return Event(
            id=ds.id,
            type=ds.type,
            show_id=ds.showId,
            show=show,
            start=dt.start,
            duration=dt.duration,
            timezone=dt.timezone,
            recurrence=dt.recurrence,
            include=dt.include,
            exclude=dt.exclude,
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

    @classmethod
    def map(cls, show: sm.Show, events: Sequence[Event] | None) -> Self:
        """Map from internal representation."""
        return cls(
            id=show.id, title=show.title, description=show.description, events=events
        )


ShowWhereInput = st.ShowWhereInput

ShowInclude = st.ShowInclude

ShowWhereUniqueIdInput = st._ShowWhereUnique_id_Input  # noqa: SLF001

ShowWhereUniqueTitleInput = st._ShowWhereUnique_title_Input  # noqa: SLF001

type ShowWhereUniqueInput = ShowWhereUniqueIdInput | ShowWhereUniqueTitleInput

ShowOrderByIdInput = st._Show_id_OrderByInput  # noqa: SLF001

ShowOrderByTitleInput = st._Show_title_OrderByInput  # noqa: SLF001

ShowOrderByDescriptionInput = st._Show_description_OrderByInput  # noqa: SLF001

type ShowOrderByInput = (
    ShowOrderByIdInput | ShowOrderByTitleInput | ShowOrderByDescriptionInput
)

ShowCreateInput = st.ShowCreateWithoutRelationsInput

ShowUpdateInput = st.ShowUpdateManyMutationInput


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
    """Show that was created."""


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
