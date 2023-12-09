from uuid import UUID

from pydantic import Field

from emishows.models.base import SerializableModel
from emishows.shows import models as sm

ListLimitParameter = int | None

ListOffsetParameter = int | None

ListWhereParameter = sm.ShowWhereInput | None

ListIncludeParameter = sm.ShowInclude | None

ListOrderParameter = sm.ShowOrderByInput | list[sm.ShowOrderByInput] | None


class ListResponse(SerializableModel):
    """Response from GET /shows."""

    count: int = Field(
        ...,
        title="ListResponse.Count",
        description="Number of shows that matched the request.",
    )
    limit: int | None = Field(
        ...,
        title="ListResponse.Limit",
        description="Maximum number of returned shows.",
    )
    offset: int | None = Field(
        ...,
        title="ListResponse.Offset",
        description="Number of shows skipped.",
    )
    shows: list[sm.Show] = Field(
        ...,
        title="ListResponse.Shows",
        description="Shows that matched the request.",
    )


class NonRecursiveListResponse(SerializableModel):
    """Non-recursive response from GET /shows."""

    count: int = Field(
        ...,
        title="NonRecursiveListResponse.Count",
        description="Number of shows that matched the request.",
    )
    limit: int | None = Field(
        ...,
        title="NonRecursiveListResponse.Limit",
        description="Maximum number of returned shows.",
    )
    offset: int | None = Field(
        ...,
        title="NonRecursiveListResponse.Offset",
        description="Number of shows skipped.",
    )
    shows: list[sm.NonRecursiveShow] = Field(
        ...,
        title="NonRecursiveListResponse.Shows",
        description="Shows that matched the request.",
    )


GetIdParameter = UUID

GetIncludeParameter = sm.ShowInclude | None

GetResponse = sm.Show

NonRecursiveGetResponse = sm.NonRecursiveShow

CreateIncludeParameter = sm.ShowInclude | None

CreateRequest = sm.ShowCreateInput

CreateResponse = sm.Show

NonRecursiveCreateResponse = sm.NonRecursiveShow

UpdateIdParameter = UUID

UpdateIncludeParameter = sm.ShowInclude | None

UpdateRequest = sm.ShowUpdateInput

UpdateResponse = sm.Show

NonRecursiveUpdateResponse = sm.NonRecursiveShow

DeleteIdParameter = UUID
