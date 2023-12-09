from prisma import models as pm
from prisma import partials as pp
from prisma import types as pt
from pydantic import Field

from emishows.models.base import SerializableModel

# Monkey-patching to simplify types
pt.ShowOrderByInput = (
    pt._Show_id_OrderByInput
    | pt._Show_title_OrderByInput
    | pt._Show_description_OrderByInput
)
pt.EventOrderByInput = (
    pt._Event_id_OrderByInput
    | pt._Event_type_OrderByInput
    | pt._Event_showId_OrderByInput
)


EventWithoutRelations = pp.EventWithoutRelations
ShowWhereInput = pt.ShowWhereInput
ShowInclude = pt.ShowInclude
ShowOrderByInput = pt.ShowOrderByInput
Show = pm.Show
ShowWhereUniqueInput = pt.ShowWhereUniqueInput
ShowCreateInput = pt.ShowCreateInput
ShowUpdateInput = pt.ShowUpdateInput


class NonRecursiveShow(pp.ShowWithoutRelations):
    """Non-recursive show model."""

    events: list[EventWithoutRelations] | None = None


class CountRequest(SerializableModel):
    """Request to count shows."""

    where: ShowWhereInput | None = Field(
        None,
        title="CountRequest.Where",
        description="Filter to apply to shows.",
    )


class CountResponse(SerializableModel):
    """Response for counting shows."""

    count: int = Field(
        ...,
        title="CountResponse.Count",
        description="Number of shows that matched the request.",
    )


class ListRequest(SerializableModel):
    """Request to list shows."""

    limit: int | None = Field(
        None,
        title="ListRequest.Limit",
        description="Maximum number of shows to return.",
    )
    offset: int | None = Field(
        None,
        title="ListRequest.Offset",
        description="Number of shows to skip.",
    )
    where: ShowWhereInput | None = Field(
        None,
        title="ListRequest.Where",
        description="Filter to apply to shows.",
    )
    include: ShowInclude | None = Field(
        None,
        title="ListRequest.Include",
        description="Relations to include with shows.",
    )
    order: ShowOrderByInput | list[ShowOrderByInput] | None = Field(
        None,
        title="ListRequest.Order",
        description="Order to apply to shows.",
    )


class ListResponse(SerializableModel):
    """Response for listing shows."""

    shows: list[Show] = Field(
        ...,
        title="ListResponse.Shows",
        description="Shows that matched the request.",
    )


class GetRequest(SerializableModel):
    """Request to get a show."""

    where: ShowWhereUniqueInput = Field(
        ...,
        title="GetRequest.Where",
        description="Filter to apply to show.",
    )
    include: ShowInclude | None = Field(
        None,
        title="GetRequest.Include",
        description="Relations to include with show.",
    )


class GetResponse(SerializableModel):
    """Response for getting a show."""

    show: Show | None = Field(
        ...,
        title="GetResponse.Show",
        description="Show that matched the request.",
    )


class CreateRequest(SerializableModel):
    """Request to create a show."""

    data: ShowCreateInput = Field(
        ...,
        title="CreateRequest.Data",
        description="Data to use to create a show.",
    )
    include: ShowInclude | None = Field(
        None,
        title="CreateRequest.Include",
        description="Relations to include with show.",
    )


class CreateResponse(SerializableModel):
    """Response for creating a show."""

    show: Show = Field(
        ...,
        title="CreateResponse.Show",
        description="Show that was created.",
    )


class UpdateRequest(SerializableModel):
    """Request to update a show."""

    data: ShowUpdateInput = Field(
        ...,
        title="UpdateRequest.Data",
        description="Data to use to update a show.",
    )
    where: ShowWhereUniqueInput = Field(
        ...,
        title="UpdateRequest.Where",
        description="Filter to apply to show.",
    )
    include: ShowInclude | None = Field(
        None,
        title="UpdateRequest.Include",
        description="Relations to include with show.",
    )


class UpdateResponse(SerializableModel):
    """Response for updating a show."""

    show: Show | None = Field(
        ...,
        title="UpdateResponse.Show",
        description="Show that was updated.",
    )


class DeleteRequest(SerializableModel):
    """Request to delete a show."""

    where: ShowWhereUniqueInput = Field(
        ...,
        title="DeleteRequest.Where",
        description="Filter to apply to show.",
    )
    include: ShowInclude | None = Field(
        None,
        title="DeleteRequest.Include",
        description="Relations to include with show.",
    )


class DeleteResponse(SerializableModel):
    """Response for deleting a show."""

    show: Show | None = Field(
        ...,
        title="DeleteResponse.Show",
        description="Show that was deleted.",
    )
