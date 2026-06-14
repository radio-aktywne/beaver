from collections.abc import Sequence
from datetime import datetime
from typing import Literal, TypedDict

from beaver.models.base import datamodel
from beaver.services.mevents import models as em

EventType = em.EventType

Show = em.Show

Frequency = em.Frequency

Weekday = em.Weekday

WeekdayRule = em.WeekdayRule

RecurrenceRule = em.RecurrenceRule

Recurrence = em.Recurrence

Event = em.Event


@datamodel
class Instance:
    """Instance data."""

    start: datetime
    """Start datetime of the instance in event timezone."""

    end: datetime
    """End datetime of the instance in event timezone."""

    event_id: str
    """Identifier of the event that the instance belongs to."""

    event: Event | None
    """Event that the instance belongs to."""


EventRelationFilter = TypedDict(
    "EventRelationFilter",
    {
        "is": em.EventWhereInput,
        "is_not": em.EventWhereInput,
    },
    total=False,
)


class InstanceWhereInput(TypedDict, total=False):
    """Instance arguments for searching."""

    event: EventRelationFilter
    """Event relation filter."""


class InstanceWhereUniqueInput(TypedDict, total=True):
    """Instance unique arguments for searching."""

    event_id: str
    """Identifier of the event that the instance belongs to."""

    start: datetime
    """Start datetime of the instance in event timezone."""


class EventArgsFromInstance(TypedDict, total=False):
    """Event arguments to include when querying instances."""

    include: em.EventInclude
    """Relations to include when querying events from instances."""


class InstanceInclude(TypedDict, total=False):
    """Relations to include when querying instances."""

    event: bool | EventArgsFromInstance
    """Event relation to include."""


type SortOrder = Literal["asc", "desc"]


class InstanceOrderByStartInput(TypedDict, total=True):
    """Order by start datetime of the instance."""

    start: SortOrder
    """Order for start datetime of the instance."""


class InstanceOrderByEndInput(TypedDict, total=True):
    """Order by end datetime of the instance."""

    end: SortOrder
    """Order for end datetime of the instance."""


type InstanceOrderByInput = InstanceOrderByStartInput | InstanceOrderByEndInput


@datamodel
class ListRequest:
    """Request to list instances."""

    start: datetime
    """Start datetime in UTC to filter instances."""

    end: datetime
    """End datetime in UTC to filter instances."""

    where: InstanceWhereInput | None
    """Filter to apply to find instances."""

    include: InstanceInclude | None
    """Relations to include in the response."""

    order: InstanceOrderByInput | None
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing instances."""

    instances: Sequence[Instance]
    """List of instances that match the filter."""


@datamodel
class GetRequest:
    """Request to get an instance."""

    where: InstanceWhereUniqueInput
    """Unique filter to apply to find an instance."""

    include: InstanceInclude | None
    """Relations to include in the response."""


@datamodel
class GetResponse:
    """Response for getting an instance."""

    instance: Instance | None
    """Instance that matches the filter."""
