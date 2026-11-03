import asyncio
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from datetime import timedelta

from beaver.config.models import CoordinationConfig
from beaver.services.consistency.coordination import errors as e, models as m
from beaver.services.consistency.reconciliation import errors as re
from beaver.services.consistency.reconciliation.service import ReconciliationService
from beaver.services.data.howlite.service import HowliteService
from beaver.services.data.sapphire import errors as se
from beaver.services.data.sapphire.service import SapphireService


class CoordinationService:
    """Service for cross-store coordination."""

    def __init__(
        self,
        config: CoordinationConfig,
        howlite: HowliteService,
        sapphire: SapphireService,
    ) -> None:
        self._config = config
        self._howlite = howlite
        self._reconciliation = ReconciliationService()
        self._sapphire = sapphire

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except (TimeoutError, re.ServiceError, se.ServiceError) as ex:
            raise e.ServiceError from ex

    async def _lock(self, transaction: m.Transaction) -> None:
        # Select an integer because Prisma cannot deserialize PostgreSQL void
        await transaction.sapphire.query_raw(
            "SELECT 1 AS locked FROM pg_advisory_xact_lock(1::bigint)"
        )

    @asynccontextmanager
    async def transaction(
        self, transaction: m.Transaction | None = None
    ) -> AsyncGenerator[m.Transaction]:
        """Open or reuse a coordinated transaction."""
        if transaction is not None:
            yield transaction
            return

        lifetime = timedelta(seconds=self._config.timeout + self._config.grace)

        with self._handle_errors():
            async with (
                self._sapphire.tx(timeout=lifetime) as sapphire,
                asyncio.timeout(self._config.timeout),
            ):
                transaction = m.Transaction(howlite=self._howlite, sapphire=sapphire)

                await self._lock(transaction)
                await self._reconciliation.reconcile(transaction)
                yield transaction
