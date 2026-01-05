class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when input fails validation."""


class DifferentTimezonesError(ValidationError):
    """Exception raised when datetimes have different timezones."""

    def __init__(self) -> None:
        super().__init__("All datetimes must have the same timezone.")
