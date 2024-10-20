from litestar.datastructures import State as LitestarState

from emishows.config.models import Config
from emishows.services.datashows.service import DatashowsService
from emishows.services.datatimes.service import DatatimesService


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    config: Config
    """Configuration for the service."""

    datashows: DatashowsService
    """Service for datashows database."""

    datatimes: DatatimesService
    """Service for datatimes database."""
