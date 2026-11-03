class ServiceError(Exception):
    """Base class for howlite service errors."""


class NotFoundError(ServiceError):
    """Raised when a resource is not found."""


class UnexpectedStatusError(ServiceError):
    """Raised when CalDAV returns an unexpected status."""

    def __init__(self, status: int) -> None:
        super().__init__(f"Unexpected CalDAV status: {status}")


class IncompleteCalendarListingError(ServiceError):
    """Raised when a calendar resource listing is incomplete."""

    def __init__(self) -> None:
        super().__init__("Incomplete calendar resource listing.")


class MissingCalendarResourceTypeError(ServiceError):
    """Raised when a listed resource has no resource type."""

    def __init__(self) -> None:
        super().__init__("Missing calendar resource type.")


class MissingQueryResponseBodyError(ServiceError):
    """Raised when a calendar query response has no body."""

    def __init__(self) -> None:
        super().__init__("Missing calendar query response body.")


class MissingCalendarDataError(ServiceError):
    """Raised when a query result has no calendar data."""

    def __init__(self) -> None:
        super().__init__("Missing calendar data in query response.")


class UnknownQueryTypeError(ServiceError, TypeError):
    """Raised when an unsupported query type is supplied."""

    def __init__(self, query_type: type) -> None:
        super().__init__(f"Unknown query type: {query_type}")
