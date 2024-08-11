class ServiceError(Exception):
    """Base class for service errors."""

    pass


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""

    pass


class DatashowsError(ServiceError):
    """Raised when a datashows database error occurs."""

    pass


class DatatimesError(ServiceError):
    """Raised when an datatimes database error occurs."""

    pass
