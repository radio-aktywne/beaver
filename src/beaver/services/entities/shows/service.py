from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from beaver.services.consistency.coordination import errors as ce, models as cm
from beaver.services.consistency.coordination.service import CoordinationService
from beaver.services.entities.shows import errors as e, models as m
from beaver.services.persistence.service import PersistenceService
from beaver.services.persistence.shows import errors as pe


class ShowsService:
    """Service to manage shows."""

    def __init__(self, coordination: CoordinationService) -> None:
        self._coordination = coordination

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except pe.ConflictError as ex:
            raise e.ConflictError from ex
        except pe.ValidationError as ex:
            raise e.ValidationError from ex
        except (ce.ServiceError, pe.ServiceError) as ex:
            raise e.ServiceError from ex

    @asynccontextmanager
    async def _transaction(
        self, transaction: cm.Transaction | None = None
    ) -> AsyncGenerator[cm.Transaction]:
        with self._handle_errors():
            async with self._coordination.transaction(transaction) as active:
                yield active

    async def count(
        self, request: m.CountRequest, *, transaction: cm.Transaction | None = None
    ) -> m.CountResponse:
        """Count shows."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            count = await persistence.shows.count(request.where)

        return m.CountResponse(count=count)

    async def list(
        self, request: m.ListRequest, *, transaction: cm.Transaction | None = None
    ) -> m.ListResponse:
        """List shows."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            shows = await persistence.shows.list(
                where=request.where,
                include=request.include,
                take=request.limit,
                skip=request.offset,
                order=request.order,
            )

        return m.ListResponse(shows=shows)

    async def get(
        self, request: m.GetRequest, *, transaction: cm.Transaction | None = None
    ) -> m.GetResponse:
        """Get show."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            show = await persistence.shows.get(request.where, include=request.include)

        return m.GetResponse(show=show)

    async def create(
        self, request: m.CreateRequest, *, transaction: cm.Transaction | None = None
    ) -> m.CreateResponse:
        """Create show."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            show = await persistence.shows.create(request.data, include=request.include)

        return m.CreateResponse(show=show)

    async def update(
        self, request: m.UpdateRequest, *, transaction: cm.Transaction | None = None
    ) -> m.UpdateResponse:
        """Update show."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            show = await persistence.shows.update(
                request.data, where=request.where, include=request.include
            )

        return m.UpdateResponse(show=show)

    async def delete(
        self, request: m.DeleteRequest, *, transaction: cm.Transaction | None = None
    ) -> m.DeleteResponse:
        """Delete show."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            show = await persistence.shows.delete(
                request.where, include=request.include
            )

        return m.DeleteResponse(show=show)
