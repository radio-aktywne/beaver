from collections.abc import Generator
from contextlib import contextmanager

from beaver.api.routes.instances import errors as e
from beaver.api.routes.instances import models as m
from beaver.services.instances import errors as ie
from beaver.services.instances import models as im
from beaver.services.instances.service import InstancesService
from beaver.utils.time import naiveutcnow


class Service:
    """Service for the instances endpoint."""

    def __init__(self, instances: InstancesService) -> None:
        self._instances = instances

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ie.ValidationError as ex:
            raise e.ValidationError from ex
        except ie.ServiceError as ex:
            raise e.ServiceError from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List instances."""
        now = naiveutcnow()

        list_request = im.ListRequest(
            start=request.start if request.start is not None else now,
            end=request.end if request.end is not None else now,
            where=request.where,
            include=request.include,
            order=request.order,
        )

        with self._handle_errors():
            list_response = await self._instances.list(list_request)

        return m.ListResponse(
            results=m.InstanceList(
                count=len(list_response.instances),
                instances=[
                    m.Instance.map(instance) for instance in list_response.instances
                ],
            )
        )
