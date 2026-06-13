from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"Event not found: {event_id}.")
