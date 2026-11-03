from beaver.services.consistency.coordination import models as cm
from beaver.services.persistence.events.service import (
    EventsPersistenceService,
)
from beaver.services.persistence.shows.service import (
    ShowsPersistenceService,
)


class PersistenceService:
    """Access complete records within an active coordinated transaction."""

    def __init__(self, transaction: cm.Transaction) -> None:
        self._events = EventsPersistenceService(transaction)
        self._shows = ShowsPersistenceService(transaction)

    @property
    def events(self) -> EventsPersistenceService:
        """Persistence operations for events."""
        return self._events

    @property
    def shows(self) -> ShowsPersistenceService:
        """Persistence operations for shows."""
        return self._shows
