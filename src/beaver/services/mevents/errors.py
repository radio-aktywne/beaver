class ServiceError(Exception):
    """Base class for service errors."""

    pass


class ValidationError(ServiceError):
    """Raised when a request fails validation."""

    pass


class HowliteError(ServiceError):
    """Raised when a howlite database operation fails."""

    pass


class SapphireError(ServiceError):
    """Raised when a sapphire database operation fails."""

    pass
