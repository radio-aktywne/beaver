from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""

    pass


class ShowNotFoundError(ServiceError):
    """Raised when show is not found."""

    def __init__(self, id: UUID) -> None:
        super().__init__(f"Show not found: {id}.")


class HowliteError(ServiceError):
    """Raised when an howlite database error occurs."""

    pass


class SapphireError(ServiceError):
    """Raised when a sapphire database error occurs."""

    pass
