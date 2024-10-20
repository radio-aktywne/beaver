from datetime import UTC, datetime

import recurring_ical_events
from icalendar import Event as vEvent
from icalendar import vDatetime
from zoneinfo import ZoneInfo

from beaver.services.icalendar import models as m
from beaver.services.icalendar.parser import ICalendarParser


class EventExpander:
    """Expands recurring iCalendar events into instances."""

    def __init__(self, parser: ICalendarParser) -> None:
        self._parser = parser

    def _normalize_datetime(self, dt: vDatetime, tz: ZoneInfo) -> datetime:
        dt = self._parser.ical_to_datetime(dt)
        dt = dt.astimezone(tz)
        return dt.replace(tzinfo=None)

    def _build_instance(self, vevent: vEvent, tz: ZoneInfo) -> m.EventInstance:
        start = self._normalize_datetime(vevent["DTSTART"], tz)
        end = self._normalize_datetime(vevent["DTEND"], tz)

        return m.EventInstance(
            start=start,
            end=end,
        )

    def expand(
        self, event: m.Event, start: datetime, end: datetime
    ) -> list[m.EventInstance]:
        """Expand the event into instances between start and end."""

        tz = event.timezone

        start = start.replace(tzinfo=UTC)
        end = end.replace(tzinfo=UTC)

        calendar = m.Calendar(
            events=[event],
        )
        calendar = self._parser.calendar_to_ical(calendar)

        vevents = recurring_ical_events.of(calendar).between(start, end)

        return [self._build_instance(vevent, tz) for vevent in vevents]
