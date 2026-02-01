class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class HowliteError(ServiceError):
    """Raised when a howlite database operation fails."""


class SapphireError(ServiceError):
    """Raised when a sapphire database operation fails."""
