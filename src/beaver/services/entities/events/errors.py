class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class PartialUpdateInsufficientDataError(ValidationError):
    """Raised when a partial update is attempted with insufficient data."""

    def __init__(self) -> None:
        super().__init__(
            "Provided data is insufficient for a partial update in the current resource state."
        )
