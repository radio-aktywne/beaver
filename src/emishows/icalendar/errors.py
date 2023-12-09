class ICalendarParserError(Exception):
    """Base class for exceptions in iCalendar parser."""

    pass


class DifferentTimezonesError(ICalendarParserError, ValueError):
    """Exception raised when datetimes have different timezones."""

    def __init__(self) -> None:
        super().__init__("All datetimes must have the same timezone.")
