from collections.abc import Generator
from contextlib import contextmanager, suppress
from uuid import UUID

from beaver.services.consistency.coordination import models as cm
from beaver.services.consistency.reconciliation import errors as e
from beaver.services.data.howlite import errors as he, models as hm
from beaver.services.data.sapphire import errors as se


class ReconciliationService:
    """Service for cross-store reconciliation."""

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except (he.ServiceError, se.ServiceError) as ex:
            raise e.ServiceError from ex

    async def _reconcile_events(self, transaction: cm.Transaction) -> None:
        events = await transaction.sapphire.event.find_many()
        sapphire_ids = {UUID(event.id) for event in events}

        response = await transaction.howlite.list_events(hm.ListEventsRequest())
        howlite_ids = response.ids

        if event_ids := sapphire_ids - howlite_ids:
            await transaction.sapphire.event.delete_many(
                where={"id": {"in": [str(event_id) for event_id in event_ids]}}
            )

        for event_id in howlite_ids - sapphire_ids:
            with suppress(he.NotFoundError):
                await transaction.howlite.delete_event(
                    hm.DeleteEventRequest(id=event_id)
                )

    async def reconcile(self, transaction: cm.Transaction) -> None:
        """Reconcile data across both stores."""
        with self._handle_errors():
            await self._reconcile_events(transaction)
