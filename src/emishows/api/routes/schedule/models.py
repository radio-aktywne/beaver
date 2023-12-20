from pydantic import Field, NaiveDatetime

from emishows.events import models as em
from emishows.icalendar import models as im
from emishows.models.base import SerializableModel

ListStartParameter = NaiveDatetime | None

ListEndParameter = NaiveDatetime | None

ListLimitParameter = int | None

ListOffsetParameter = int | None

ListWhereParameter = em.EventWhereInput | None

ListIncludeParameter = em.EventInclude | None

ListOrderParameter = em.EventOrderByInput | list[em.EventOrderByInput] | None


class EventSchedule(SerializableModel):
    """Event schedule."""

    event: em.Event = Field(
        ...,
        title="EventSchedule.Event",
        description="Event.",
    )
    instances: list[im.EventInstance] = Field(
        ...,
        title="EventSchedule.Instances",
        description="Event instances.",
    )


class ListResponse(SerializableModel):
    """Response from GET /schedule."""

    count: int = Field(
        ...,
        title="ListResponse.Count",
        description="Number of event schedules that matched the request.",
    )
    limit: int | None = Field(
        ...,
        title="ListResponse.Limit",
        description="Maximum number of returned event schedules.",
    )
    offset: int | None = Field(
        ...,
        title="ListResponse.Offset",
        description="Number of event schedules skipped.",
    )
    schedules: list[EventSchedule] = Field(
        ...,
        title="ListResponse.Schedules",
        description="Event schedules that matched the request.",
    )
