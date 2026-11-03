from collections.abc import Sequence, Set as AbstractSet
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from beaver.models.base import datamodel
from beaver.services.data.howlite import models as hm
from beaver.services.data.sapphire import enums as se, models as sm


SapphireEvent = sm.Event

SapphireShow = sm.Show

EventType = se.EventType

Frequency = hm.Frequency

Weekday = hm.Weekday

CountTermination = hm.CountTermination

UntilTermination = hm.UntilTermination

type Termination = hm.Termination

WeekdayRule = hm.WeekdayRule

Recurrence = hm.Recurrence

Inclusion = hm.Inclusion

Exclusion = hm.Exclusion


@datamodel
class Show:
    """A show with its requested event relations."""

    id: str
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    events: Sequence[Event] | None
    """Events belonging to the show, when requested."""


@datamodel
class Event:
    """An event assembled from both stores."""

    id: str
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show_id: str | None
    """Identifier of the show the event belongs to."""

    show: Show | None
    """Show the event belongs to, when requested."""

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
