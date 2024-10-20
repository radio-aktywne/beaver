from collections.abc import Generator
from contextlib import contextmanager

from beaver.api.routes.shows import errors as e
from beaver.api.routes.shows import models as m
from beaver.services.shows import errors as se
from beaver.services.shows import models as sm
from beaver.services.shows.service import ShowsService


class Service:
    """Service for the shows endpoint."""

    def __init__(self, shows: ShowsService) -> None:
        self._shows = shows

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except se.ValidationError as ex:
            raise e.ValidationError(str(ex)) from ex
        except se.HowliteError as ex:
            raise e.HowliteError(str(ex)) from ex
        except se.SapphireError as ex:
            raise e.SapphireError(str(ex)) from ex
        except se.ServiceError as ex:
            raise e.ServiceError(str(ex)) from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List shows."""

        limit = request.limit
        offset = request.offset
        where = request.where
        include = request.include
        order = request.order

        req = sm.CountRequest(
            where=where,
        )

        with self._handle_errors():
            res = await self._shows.count(req)

        count = res.count

        req = sm.ListRequest(
            limit=limit,
            offset=offset,
            where=where,
            include=include,
            order=order,
        )

        with self._handle_errors():
            res = await self._shows.list(req)

        shows = res.shows

        shows = [m.Show.map(show) for show in shows]
        results = m.ShowList(
            count=count,
            limit=limit,
            offset=offset,
            shows=shows,
        )
        return m.ListResponse(
            results=results,
        )

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get show."""

        id = request.id
        include = request.include

        req = sm.GetRequest(
            where={
                "id": str(id),
            },
            include=include,
        )

        with self._handle_errors():
            res = await self._shows.get(req)

        show = res.show

        if show is None:
            raise e.ShowNotFoundError(id)

        show = m.Show.map(show)
        return m.GetResponse(
            show=show,
        )

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create show."""

        data = request.data
        include = request.include

        req = sm.CreateRequest(
            data=data,
            include=include,
        )

        with self._handle_errors():
            res = await self._shows.create(req)

        show = res.show

        show = m.Show.map(show)
        return m.CreateResponse(
            show=show,
        )

    async def update(self, request: m.UpdateRequest) -> m.UpdateResponse:
        """Update show."""

        data = request.data
        id = request.id
        include = request.include

        req = sm.UpdateRequest(
            data=data,
            where={
                "id": str(id),
            },
            include=include,
        )

        with self._handle_errors():
            res = await self._shows.update(req)

        show = res.show

        if show is None:
            raise e.ShowNotFoundError(id)

        show = m.Show.map(show)
        return m.UpdateResponse(
            show=show,
        )

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete show."""

        id = request.id

        req = sm.DeleteRequest(
            where={
                "id": str(id),
            },
            include=None,
        )

        with self._handle_errors():
            res = await self._shows.delete(req)

        show = res.show

        if show is None:
            raise e.ShowNotFoundError(id)

        return m.DeleteResponse()
