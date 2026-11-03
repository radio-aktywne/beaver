from beaver.models.base import datamodel
from beaver.services.data.howlite.service import HowliteService
from beaver.services.data.sapphire.service import SapphireService


@datamodel
class Transaction:
    """Coordinated transaction."""

    howlite: HowliteService
    """Service for howlite database."""

    sapphire: SapphireService
    """Service for sapphire database."""
