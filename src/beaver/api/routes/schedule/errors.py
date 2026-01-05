class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class HowliteError(ServiceError):
    """Raised when an howlite database error occurs."""


class SapphireError(ServiceError):
    """Raised when a sapphire database error occurs."""
