from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""

    pass


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""

    def __init__(self, id: UUID) -> None:
        super().__init__(f"Event not found: {id}.")


class DatashowsError(ServiceError):
    """Raised when a datashows database error occurs."""

    pass


class DatatimesError(ServiceError):
    """Raised when an datatimes database error occurs."""

    pass
