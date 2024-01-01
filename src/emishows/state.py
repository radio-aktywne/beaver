from litestar.datastructures import State as LitestarState
from prisma import Prisma

from emishows.config.models import Config
from emishows.emitimes.service import EmitimesService


class State(LitestarState):
    """Use this class as a type hint for the state of your application.

    Attributes:
        config: Configuration for the application.
        prisma: Database client.
        emitimes: Service for emitimes API.
    """

    config: Config
    prisma: Prisma
    emitimes: EmitimesService
