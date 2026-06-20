from datetime import datetime

from beaver.utils.time import isostringify


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class EventDoesNotExistError(ValidationError):
    """Raised when an event does not exist."""

    def __init__(self, event_id: str) -> None:
        super().__init__(f"Event with id {event_id} does not exist.")


class ConflictError(ValidationError):
    """Raised when a conflict error occurs."""


class InstanceAlreadyExistsError(ConflictError):
    """Raised when an instance already exists."""

    def __init__(self, event_id: str, start: datetime) -> None:
        super().__init__(
            f"Instance with start {isostringify(start)} already exists for event {event_id}."
        )
