class ServiceError(Exception):
    """Base class for service errors."""

    def __init__(self, message: str | None = None) -> None:
        self._message = message

        args = (message,) if message else ()
        super().__init__(*args)

    @property
    def message(self) -> str | None:
        return self._message


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""

    pass


class NotFoundError(ServiceError):
    """Raised when a resource is not found."""

    pass


class DatashowsError(ServiceError):
    """Raised when a datashows database error occurs."""

    pass
