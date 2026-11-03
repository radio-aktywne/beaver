from collections.abc import Sequence

from beaver.models.base import datamodel
from beaver.services.persistence.shows import models as pm


EventType = pm.EventType

Frequency = pm.Frequency

Weekday = pm.Weekday

CountTermination = pm.CountTermination

UntilTermination = pm.UntilTermination

type Termination = pm.Termination

WeekdayRule = pm.WeekdayRule

Recurrence = pm.Recurrence

Inclusion = pm.Inclusion

Exclusion = pm.Exclusion

Event = pm.Event

Show = pm.Show

ShowWhereInput = pm.ShowWhereInput

ShowInclude = pm.ShowInclude

ShowWhereUniqueIdInput = pm.ShowWhereUniqueIdInput

ShowWhereUniqueTitleInput = pm.ShowWhereUniqueTitleInput

type ShowWhereUniqueInput = ShowWhereUniqueIdInput | ShowWhereUniqueTitleInput

ShowOrderByIdInput = pm.ShowOrderByIdInput

ShowOrderByTitleInput = pm.ShowOrderByTitleInput

ShowOrderByDescriptionInput = pm.ShowOrderByDescriptionInput

type ShowOrderByInput = (
    ShowOrderByIdInput | ShowOrderByTitleInput | ShowOrderByDescriptionInput
)

ShowCreateInput = pm.ShowCreateInput

ShowUpdateInput = pm.ShowUpdateInput


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
