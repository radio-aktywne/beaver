from datetime import timezone

import recurring_ical_events
from icalendar import Event as vEvent
from icalendar import vDatetime
from pydantic import NaiveDatetime
from zoneinfo import ZoneInfo

from emishows.icalendar.models import Calendar, Event, EventInstance
from emishows.icalendar.parser import ICalendarParser


class EventExpander:
    def __init__(self) -> None:
        self._parser = ICalendarParser()

    def _normalize_datetime(
        self, datetime: vDatetime, timezone: ZoneInfo
    ) -> NaiveDatetime:
        """Normalize a datetime."""

        datetime = self._parser.ical_to_datetime(datetime)
        datetime = datetime.astimezone(timezone)
        return datetime.replace(tzinfo=None)

    def _build_instance(self, vevent: vEvent, timezone: ZoneInfo) -> EventInstance:
        """Build an instance from an event."""

        start = self._normalize_datetime(vevent["DTSTART"], timezone)
        end = self._normalize_datetime(vevent["DTEND"], timezone)

        return EventInstance(start=start, end=end)

    def expand(
        self, event: Event, start: NaiveDatetime, end: NaiveDatetime
    ) -> list[EventInstance]:
        """Expand the event into instances between start and end."""

        tz = ZoneInfo(event.timezone)

        start = start.replace(tzinfo=timezone.utc)
        end = end.replace(tzinfo=timezone.utc)

        calendar = Calendar(events=[event])
        calendar = self._parser.calendar_to_ical(calendar)

        vevents = recurring_ical_events.of(calendar).between(start, end)

        return [self._build_instance(vevent, tz) for vevent in vevents]
