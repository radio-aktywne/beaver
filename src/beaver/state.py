from litestar.datastructures import State as LitestarState

from beaver.config.models import Config
from beaver.services.howlite.service import HowliteService
from beaver.services.sapphire.service import SapphireService


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    config: Config
    """Configuration for the service."""

    howlite: HowliteService
    """Service for howlite database."""

    sapphire: SapphireService
    """Service for sapphire database."""
