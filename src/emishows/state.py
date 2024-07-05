from litestar.datastructures import State as LitestarState
from prisma import Prisma

from emishows.config.models import Config
from emishows.datatimes.service import DatatimesService


class State(LitestarState):
    """Use this class as a type hint for the state of your application.

    Attributes:
        config: Configuration for the application.
        prisma: Datashows database client.
        datatimes: Service for datatimes API.
    """

    config: Config
    prisma: Prisma
    datatimes: DatatimesService
