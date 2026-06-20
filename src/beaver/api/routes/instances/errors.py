from datetime import datetime
from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class ConflictError(ValidationError):
    """Raised when a conflict error occurs."""


class InstanceNotFoundError(ServiceError):
    """Raised when instance is not found."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(
            f"Instance not found for event {event} at {start.isoformat()}."
        )
