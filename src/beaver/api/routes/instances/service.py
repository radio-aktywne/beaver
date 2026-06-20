from collections.abc import Generator
from contextlib import contextmanager

from beaver.api.routes.instances import errors as e
from beaver.api.routes.instances import models as m
from beaver.services.entities.instances import errors as ie
from beaver.services.entities.instances import models as im
from beaver.services.entities.instances.service import InstancesService


class Service:
    """Service for the instances endpoint."""

    def __init__(self, instances: InstancesService) -> None:
        self._instances = instances

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ie.ConflictError as ex:
            raise e.ConflictError from ex
        except ie.ValidationError as ex:
            raise e.ValidationError from ex
        except ie.ServiceError as ex:
            raise e.ServiceError from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List instances."""
        list_request = im.ListRequest(
            start=request.start,
            end=request.end,
            where=request.where,
            include=request.include,
            order=request.order,
        )

        with self._handle_errors():
            list_response = await self._instances.list(list_request)

        return m.ListResponse(
            results=m.InstanceList(
                start=request.start,
                end=request.end,
                instances=[
                    m.Instance.map(instance) for instance in list_response.instances
                ],
            )
        )

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get instance."""
        get_request = im.GetRequest(
            where={"event_id": str(request.event_id), "start": request.start},
            include=request.include,
        )

        with self._handle_errors():
            get_response = await self._instances.get(get_request)

        if get_response.instance is None:
            raise e.InstanceNotFoundError(request.event_id, request.start)

        return m.GetResponse(instance=m.Instance.map(get_response.instance))
