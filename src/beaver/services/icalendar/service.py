from beaver.services.icalendar.expander import EventExpander
from beaver.services.icalendar.parser import ICalendarParser


class ICalendarService:
    """Service for handling iCalendar operations."""

    def __init__(self) -> None:
        self._parser = ICalendarParser()
        self._expander = EventExpander(self._parser)

    @property
    def parser(self) -> ICalendarParser:
        """Parser for iCalendar objects."""
        return self._parser

    @property
    def expander(self) -> EventExpander:
        """Expander for recurring iCalendar events."""
        return self._expander
