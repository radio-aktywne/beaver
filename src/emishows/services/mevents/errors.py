class ServiceError(Exception):
    """Base class for service errors."""

    pass


class ValidationError(ServiceError):
    """Raised when a request fails validation."""

    pass


class DatashowsError(ServiceError):
    """Raised when a datashows database operation fails."""

    pass


class DatatimesError(ServiceError):
    """Raised when a datatimes database operation fails."""

    pass
