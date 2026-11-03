from collections.abc import Generator, Sequence
from contextlib import contextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

import recurring_ical_events
from icalendar import Event as vEvent

from beaver.services.icalendar import errors as e, models as m
from beaver.services.icalendar.parser import ICalendarParser


class EventExpander:
    """Expands recurring iCalendar events into instances."""

    def __init__(self, parser: ICalendarParser) -> None:
        self._parser = parser

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ValueError as ex:
            raise e.ValidationError from ex

    def _build_instance(self, vevent: vEvent, tz: ZoneInfo) -> m.Instance:
        return m.Instance(
            start=vevent.start.astimezone(tz).replace(tzinfo=None)
            if isinstance(vevent.start, datetime)
            else datetime.combine(vevent.start, datetime.min.time(), tzinfo=None),
            duration=vevent.duration,
        )

    def expand(
        self, event: m.Event, start: datetime, end: datetime
    ) -> Sequence[m.Instance]:
        """Expand the event into instances between start and end."""
        with self._handle_errors():
            calendar = self._parser.calendar_to_ical(m.Calendar(events=[event]))
            components = recurring_ical_events.of(calendar).between(start, end)
            return [
                self._build_instance(component, event.timezone)
                for component in components
                if isinstance(component, vEvent)
            ]
