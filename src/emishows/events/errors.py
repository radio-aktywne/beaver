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


class DatashowsError(ServiceError):
    """Raised when a datashows database operation fails."""

    pass


class DatatimesError(ServiceError):
    """Raised when an operation with datatimes API fails."""

    pass
