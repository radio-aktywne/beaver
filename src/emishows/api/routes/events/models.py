from uuid import UUID

from pydantic import Field

from emishows.events import models as em
from emishows.models.base import SerializableModel

ListLimitParameter = int | None

ListOffsetParameter = int | None

ListWhereParameter = em.EventWhereInput | None

ListQueryParameter = em.Query | None

ListIncludeParameter = em.EventInclude | None

ListOrderParameter = em.EventOrderByInput | list[em.EventOrderByInput] | None


class ListResponse(SerializableModel):
    """Response from GET /events."""

    count: int = Field(
        ...,
        title="ListResponse.Count",
        description="Number of events that matched the request.",
    )
    limit: int | None = Field(
        ...,
        title="ListResponse.Limit",
        description="Maximum number of returned events.",
    )
    offset: int | None = Field(
        ...,
        title="ListResponse.Offset",
        description="Number of events skipped.",
    )
    events: list[em.Event] = Field(
        ...,
        title="ListResponse.Events",
        description="Events that matched the request.",
    )


GetIdParameter = UUID

GetIncludeParameter = em.EventInclude | None

GetResponse = em.Event

CreateIncludeParameter = em.EventInclude | None

CreateRequest = em.EventCreateInput

CreateResponse = em.Event

UpdateIdParameter = UUID

UpdateIncludeParameter = em.EventInclude | None

UpdateRequest = em.EventUpdateInput

UpdateResponse = em.Event

DeleteIdParameter = UUID

DeleteResponse = None
