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
            raise e.ValidationError from ex
        except se.HowliteError as ex:
            raise e.HowliteError from ex
        except se.SapphireError as ex:
            raise e.SapphireError from ex
        except se.ServiceError as ex:
            raise e.ServiceError from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List shows."""
        count_request = sm.CountRequest(
            where=request.where,
        )

        with self._handle_errors():
            count_response = await self._shows.count(count_request)

        list_request = sm.ListRequest(
            limit=request.limit,
            offset=request.offset,
            where=request.where,
            include=request.include,
            order=request.order,
        )

        with self._handle_errors():
            list_response = await self._shows.list(list_request)

        return m.ListResponse(
            results=m.ShowList(
                count=count_response.count,
                limit=request.limit,
                offset=request.offset,
                shows=[m.Show.map(show) for show in list_response.shows],
            )
        )

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get show."""
        get_request = sm.GetRequest(
            where={
                "id": str(request.id),
            },
            include=request.include,
        )

        with self._handle_errors():
            get_response = await self._shows.get(get_request)

        if get_response.show is None:
            raise e.ShowNotFoundError(request.id)

        return m.GetResponse(show=m.Show.map(get_response.show))

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create show."""
        create_request = sm.CreateRequest(
            data=request.data,
            include=request.include,
        )

        with self._handle_errors():
            create_response = await self._shows.create(create_request)

        return m.CreateResponse(show=m.Show.map(create_response.show))

    async def update(self, request: m.UpdateRequest) -> m.UpdateResponse:
        """Update show."""
        update_request = sm.UpdateRequest(
            data=request.data,
            where={
                "id": str(request.id),
            },
            include=request.include,
        )

        with self._handle_errors():
            update_response = await self._shows.update(update_request)

        if update_response.show is None:
            raise e.ShowNotFoundError(request.id)

        return m.UpdateResponse(show=m.Show.map(update_response.show))

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete show."""
        delete_request = sm.DeleteRequest(
            where={
                "id": str(request.id),
            },
            include=None,
        )

        with self._handle_errors():
            delete_response = await self._shows.delete(delete_request)

        if delete_response.show is None:
            raise e.ShowNotFoundError(request.id)

        return m.DeleteResponse()
