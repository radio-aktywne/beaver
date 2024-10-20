class ServiceError(Exception):
    """Base class for service errors."""

    pass


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""

    pass


class HowliteError(ServiceError):
    """Raised when an howlite database error occurs."""

    pass


class SapphireError(ServiceError):
    """Raised when a sapphire database error occurs."""

    pass
