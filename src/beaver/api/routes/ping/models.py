from beaver.models.base import datamodel


@datamodel
class PingRequest:
    """Request to ping."""

    pass


@datamodel
class PingResponse:
    """Response for ping."""

    pass


@datamodel
class HeadPingRequest:
    """Request to ping headers."""

    pass


@datamodel
class HeadPingResponse:
    """Response for ping headers."""

    pass
