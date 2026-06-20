from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class ConflictError(ValidationError):
    """Raised when a conflict error occurs."""


class ShowNotFoundError(ServiceError):
    """Raised when show is not found."""

    def __init__(self, show_id: UUID) -> None:
        super().__init__(f"Show not found: {show_id}.")
