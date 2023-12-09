class ServiceError(Exception):
    """Base class for EventService errors."""

    def __init__(self, message: str | None = None) -> None:
        self._message = message

        args = (message,) if message else ()
        super().__init__(*args)

    @property
    def message(self) -> str | None:
        return self._message


class ValidationError(ServiceError):
    """Raised when a request fails validation."""

    pass


class DatabaseError(ServiceError):
    """Raised when a database operation fails."""

    pass


class EmitimesError(ServiceError):
    """Raised when an operation with emitimes API fails."""

    pass
