class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class DifferentTimezonesError(ValidationError):
    """Raised when datetimes have different timezones."""

    def __init__(self) -> None:
        super().__init__("All datetimes must have the same timezone.")
