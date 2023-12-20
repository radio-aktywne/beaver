from emishows.api.routes.shows import errors as e
from emishows.api.routes.shows import models as m
from emishows.shows import errors as se
from emishows.shows import models as sm
from emishows.shows.service import ShowsService


class Service:
    """Service for the shows endpoint."""

    def __init__(self, shows: ShowsService) -> None:
        self._shows = shows

    async def list(
        self,
        limit: m.ListLimitParameter,
        offset: m.ListOffsetParameter,
        where: m.ListWhereParameter,
        include: m.ListIncludeParameter,
        order: m.ListOrderParameter,
    ) -> m.ListResponse:
        """List shows."""

        request = sm.CountRequest(
            where=where,
        )

        try:
            response = await self._shows.count(request)
        except se.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except se.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except se.ServiceError as error:
            raise e.ServiceError(error.message) from error

        count = response.count

        request = sm.ListRequest(
            limit=limit,
            offset=offset,
            where=where,
            include=include,
            order=order,
        )

        try:
            response = await self._shows.list(request)
        except se.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except se.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except se.ServiceError as error:
            raise e.ServiceError(error.message) from error

        return m.ListResponse(
            count=count,
            limit=limit,
            offset=offset,
            shows=response.shows,
        )

    async def get(
        self,
        id: m.GetIdParameter,
        include: m.GetIncludeParameter,
    ) -> m.GetResponse:
        """Get a show."""

        request = sm.GetRequest(
            where={"id": str(id)},
            include=include,
        )

        try:
            response = await self._shows.get(request)
        except se.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except se.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except se.ServiceError as error:
            raise e.ServiceError(error.message) from error

        show = response.show

        if show is None:
            raise e.NotFoundError()

        return show

    async def create(
        self,
        data: m.CreateRequest,
        include: m.CreateIncludeParameter,
    ) -> m.CreateResponse:
        """Create a show."""

        request = sm.CreateRequest(
            data=data,
            include=include,
        )

        try:
            response = await self._shows.create(request)
        except se.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except se.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except se.ServiceError as error:
            raise e.ServiceError(error.message) from error

        return response.show

    async def update(
        self,
        id: m.UpdateIdParameter,
        data: m.UpdateRequest,
        include: m.UpdateIncludeParameter,
    ) -> m.UpdateResponse:
        """Update a show."""

        request = sm.UpdateRequest(
            data=data,
            where={"id": str(id)},
            include=include,
        )

        try:
            response = await self._shows.update(request)
        except se.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except se.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except se.ServiceError as error:
            raise e.ServiceError(error.message) from error

        show = response.show

        if show is None:
            raise e.NotFoundError()

        return show

    async def delete(
        self,
        id: m.DeleteIdParameter,
    ) -> m.DeleteResponse:
        """Delete a show."""

        request = sm.DeleteRequest(
            where={"id": str(id)},
        )

        try:
            response = await self._shows.delete(request)
        except se.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except se.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except se.ServiceError as error:
            raise e.ServiceError(error.message) from error

        show = response.show

        if show is None:
            raise e.NotFoundError()

        return None
