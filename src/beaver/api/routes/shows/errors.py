from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class ShowNotFoundError(ServiceError):
    """Raised when show is not found."""

    def __init__(self, show_id: UUID) -> None:
        super().__init__(f"Show not found: {show_id}.")


class HowliteError(ServiceError):
    """Raised when an howlite database error occurs."""


class SapphireError(ServiceError):
    """Raised when a sapphire database error occurs."""
