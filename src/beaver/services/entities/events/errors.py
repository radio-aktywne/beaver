from datetime import datetime

from beaver.utils.time import isostringify


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class PartialUpdateInsufficientDataError(ValidationError):
    """Raised when a partial update is attempted with insufficient data."""

    def __init__(self) -> None:
        super().__init__(
            "Provided data is insufficient for a partial update in the current resource state."
        )


class SplitOneTimeEventError(ValidationError):
    """Raised when attempting to split a one-time event."""

    def __init__(self) -> None:
        super().__init__("Cannot split a one-time event.")


class SplitInstanceMatchError(ValidationError):
    """Raised when attempting to split an event at a time that does not match any recurring instance."""

    def __init__(self, event_id: str, at: datetime) -> None:
        super().__init__(
            f"Cannot split event {event_id} at {isostringify(at)}, because it does not match any recurring instance of the event."
        )


class SplitFirstInstanceError(ValidationError):
    """Raised when attempting to split at the first instance of a recurring event."""

    def __init__(self, event_id: str, at: datetime) -> None:
        super().__init__(
            f"Cannot split event {event_id} at {isostringify(at)}, because it is the first instance of the recurring event."
        )


class ConflictError(ValidationError):
    """Raised when a conflict error occurs."""
