from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.params import Body, Parameter
from litestar.response import Response

from emishows.api.exceptions import BadRequestException, NotFoundException
from emishows.api.routes.shows import errors as e
from emishows.api.routes.shows import models as m
from emishows.api.routes.shows.service import Service
from emishows.api.validator import Validator
from emishows.services.shows.service import ShowsService
from emishows.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(
        self,
        state: State,
        channels: ChannelsPlugin,
    ) -> Service:
        return Service(
            shows=ShowsService(
                datashows=state.datashows,
                datatimes=state.datatimes,
                channels=channels,
            )
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the shows endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="List shows",
    )
    async def list(
        self,
        service: Service,
        limit: Annotated[
            m.ListRequestLimit,
            Parameter(
                description="Maximum number of shows to return.",
            ),
        ] = 10,
        offset: Annotated[
            m.ListRequestOffset,
            Parameter(
                description="Number of shows to skip.",
            ),
        ] = None,
        where: Annotated[
            str | None,
            Parameter(
                description="Filter to apply to find shows.",
            ),
        ] = None,
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
        order: Annotated[
            str | None,
            Parameter(
                description="Order to apply to the results.",
            ),
        ] = None,
    ) -> Response[m.ListResponseResults]:
        """List shows that match the request."""

        where = Validator(m.ListRequestWhere).json(where) if where else None
        include = Validator(m.ListRequestInclude).json(include) if include else None
        order = Validator(m.ListRequestOrder).json(order) if order else None

        req = m.ListRequest(
            limit=limit,
            offset=offset,
            where=where,
            include=include,
            order=order,
        )

        try:
            res = await service.list(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex

        results = res.results

        return Response(results)

    @handlers.get(
        "/{id:uuid}",
        summary="Get show",
    )
    async def get(
        self,
        service: Service,
        id: Annotated[
            m.GetRequestId,
            Parameter(
                description="Identifier of the show to get.",
            ),
        ],
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[m.GetResponseShow]:
        """Get a show by ID."""

        include = Validator(m.GetRequestInclude).json(include) if include else None

        req = m.GetRequest(
            id=id,
            include=include,
        )

        try:
            res = await service.get(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.ShowNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        show = res.show

        return Response(show)

    @handlers.post(
        summary="Create show",
    )
    async def create(
        self,
        service: Service,
        data: Annotated[
            m.CreateRequestData,
            Body(
                description="Data to create a show.",
            ),
        ],
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[m.CreateResponseShow]:
        """Create a new show."""

        data = Validator(m.CreateRequestData).object(data)
        include = Validator(m.CreateRequestInclude).json(include) if include else None

        req = m.CreateRequest(
            data=data,
            include=include,
        )

        try:
            res = await service.create(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex

        show = res.show

        return Response(show)

    @handlers.patch(
        "/{id:uuid}",
        summary="Update show",
    )
    async def update(
        self,
        service: Service,
        id: Annotated[
            m.UpdateRequestId,
            Parameter(
                description="Identifier of the show to update.",
            ),
        ],
        data: Annotated[
            m.UpdateRequestData,
            Body(
                description="Data to update a show.",
            ),
        ],
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[m.UpdateResponseShow]:
        """Update a show by ID."""

        data = Validator(m.UpdateRequestData).object(data)
        include = Validator(m.UpdateRequestInclude).json(include) if include else None

        req = m.UpdateRequest(
            data=data,
            id=id,
            include=include,
        )

        try:
            res = await service.update(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.ShowNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        show = res.show

        return Response(show)

    @handlers.delete(
        "/{id:uuid}",
        summary="Delete show",
    )
    async def delete(
        self,
        service: Service,
        id: Annotated[
            m.DeleteRequestId,
            Parameter(
                description="Identifier of the show to delete.",
            ),
        ],
    ) -> Response[None]:
        """Delete a show by ID."""

        req = m.DeleteRequest(
            id=id,
        )

        try:
            await service.delete(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.ShowNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        return Response(None)
