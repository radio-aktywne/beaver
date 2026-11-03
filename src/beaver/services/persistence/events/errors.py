class ServiceError(Exception):
    """Base class for service errors."""


class MissingHowliteEventError(ServiceError):
    """Raised when a sapphire event has no howlite counterpart."""

    def __init__(self, event_id: str) -> None:
        super().__init__(f"Missing howlite event: {event_id}")


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class PartialUpdateInsufficientDataError(ValidationError):
    """Raised when a partial update is attempted with insufficient data."""


class ConflictError(ValidationError):
    """Raised when a conflict error occurs."""
