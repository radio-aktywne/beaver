from collections.abc import AsyncGenerator, Generator, Sequence
from contextlib import asynccontextmanager, contextmanager
from datetime import UTC, datetime
from uuid import UUID

from beaver.services.consistency.coordination import errors as ce, models as cm
from beaver.services.consistency.coordination.service import CoordinationService
from beaver.services.entities.instances import errors as e, models as m
from beaver.services.icalendar import errors as ie, models as im
from beaver.services.icalendar.service import ICalendarService
from beaver.services.persistence.events import errors as pe
from beaver.services.persistence.service import PersistenceService


class InstancesService:
    """Service to manage instances."""

    def __init__(
        self,
        coordination: CoordinationService,
        icalendar: ICalendarService,
    ) -> None:
        self._coordination = coordination
        self._icalendar = icalendar

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except pe.ConflictError as ex:
            raise e.ConflictError from ex
        except (ie.ValidationError, pe.ValidationError) as ex:
            raise e.ValidationError from ex
        except (ce.ServiceError, ie.ServiceError, pe.ServiceError) as ex:
            raise e.ServiceError from ex

    @asynccontextmanager
    async def _transaction(
        self, transaction: cm.Transaction | None = None
    ) -> AsyncGenerator[cm.Transaction]:
        with self._handle_errors():
            async with self._coordination.transaction(transaction) as active:
                yield active

    def _event_where(
        self, where: m.InstanceWhereInput | None
    ) -> m.EventWhereInput | None:
        relation = where.get("event", {}) if where is not None else {}
        filters: list[m.EventWhereInput] = []
        if "is" in relation:
            filters.append(relation["is"])
        if "is_not" in relation:
            filters.append({"NOT": [relation["is_not"]]})

        if not filters:
            return None

        if len(filters) == 1:
            return filters[0]

        return {"AND": filters}

    def _event_include(
        self, include: m.InstanceInclude | None
    ) -> m.EventInclude | None:
        relation = include.get("event") if include is not None else None
        if relation is None or isinstance(relation, bool):
            return None

        return relation.get("include")

    def _map_instance(
        self, instance: im.Instance, event: m.Event, include: m.InstanceInclude | None
    ) -> m.Instance:
        relation = include.get("event") if include is not None else None

        return m.Instance(
            start=instance.start,
            duration=instance.duration,
            event_id=event.id,
            event=event if relation is not None and relation is not False else None,
        )

    def _list_event_instances(
        self, event: m.Event, start: datetime, end: datetime
    ) -> Sequence[im.Instance]:
        ievent = im.Event(
            id=UUID(event.id),
            start=event.start,
            duration=event.duration,
            timezone=event.timezone,
            recurrence=event.recurrence,
            include=event.include,
            exclude=event.exclude,
        )

        return self._icalendar.expander.expand(ievent, start, end)

    def _find_instance(self, event: m.Event, start: datetime) -> im.Instance | None:
        utc_start = start.replace(tzinfo=event.timezone).astimezone(UTC)
        instances = self._list_event_instances(event, utc_start, utc_start)

        return next(
            (instance for instance in instances if instance.start == start), None
        )

    def _sort_instances(
        self,
        instances: Sequence[m.Instance],
        order: m.InstanceOrderByInput | Sequence[m.InstanceOrderByInput] | None,
    ) -> Sequence[m.Instance]:
        result = list(instances)
        if order is None:
            return result

        if not isinstance(order, Sequence):
            order = [order]

        for item in reversed(order):
            for key, direction in item.items():
                result.sort(
                    key=lambda instance: getattr(instance, key),
                    reverse=direction == "desc",
                )

        return result

    async def list(
        self, request: m.ListRequest, *, transaction: cm.Transaction | None = None
    ) -> m.ListResponse:
        """List instances."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            events = await persistence.events.list(
                query=m.TimeRangeQuery(start=request.start, end=request.end),
                where=self._event_where(request.where),
                include=self._event_include(request.include),
            )
            instances = [
                self._map_instance(instance, event, request.include)
                for event in events
                for instance in self._list_event_instances(
                    event, request.start, request.end
                )
            ]
            result = self._sort_instances(instances, request.order)

        return m.ListResponse(instances=result)

    async def get(
        self, request: m.GetRequest, *, transaction: cm.Transaction | None = None
    ) -> m.GetResponse:
        """Get instance."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            event = await persistence.events.get(
                where={"id": request.where["event_id"]},
                include=self._event_include(request.include),
            )
            if event is None:
                return m.GetResponse(instance=None)

            instance = self._find_instance(event, request.where["start"])
            result = (
                self._map_instance(instance, event, request.include)
                if instance is not None
                else None
            )

        return m.GetResponse(instance=result)

    async def create(
        self, request: m.CreateRequest, *, transaction: cm.Transaction | None = None
    ) -> m.CreateResponse:
        """Create instance."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            event = await persistence.events.get(where={"id": request.data.event_id})
            if event is None:
                raise e.EventDoesNotExistError(request.data.event_id)

            if self._find_instance(event, request.data.start) is not None:
                raise e.InstanceAlreadyExistsError(event.id, request.data.start)

            event = await persistence.events.update(
                data={
                    "include": (event.include or set())
                    | {m.Inclusion(start=request.data.start)},
                    "exclude": (event.exclude or set())
                    - {m.Exclusion(start=request.data.start)},
                },
                where={"id": event.id},
                include=self._event_include(request.include),
            )
            if event is None:
                raise e.EventDoesNotExistError(request.data.event_id)

            instance = self._find_instance(event, request.data.start)
            if instance is None:
                raise e.InstanceNotProducedError(event.id, request.data.start)

            result = self._map_instance(instance, event, request.include)

        return m.CreateResponse(instance=result)

    async def update(
        self, request: m.UpdateRequest, *, transaction: cm.Transaction | None = None
    ) -> m.UpdateResponse:
        """Update instance."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            where: m.EventWhereUniqueInput = {"id": request.where["event_id"]}
            event = await persistence.events.get(where)
            if event is None:
                return m.UpdateResponse(instance=None)

            instance = self._find_instance(event, request.where["start"])
            if instance is None:
                return m.UpdateResponse(instance=None)

            start = request.data.get("start", instance.start)
            include = self._event_include(request.include)
            if start == instance.start:
                if include is not None:
                    event = await persistence.events.get(where, include=include)
                    if event is None:
                        return m.UpdateResponse(instance=None)
                return m.UpdateResponse(
                    instance=self._map_instance(instance, event, request.include)
                )

            if self._find_instance(event, start) is not None:
                raise e.InstanceAlreadyExistsError(event.id, start)

            event = await persistence.events.update(
                data={
                    "include": (event.include or set()) | {m.Inclusion(start=start)},
                    "exclude": (
                        (event.exclude or set()) | {m.Exclusion(start=instance.start)}
                    )
                    - {m.Exclusion(start=start)},
                },
                where=where,
                include=include,
            )
            if event is None:
                return m.UpdateResponse(instance=None)

            instance = self._find_instance(event, start)
            if instance is None:
                raise e.InstanceNotProducedError(event.id, start)

            result = self._map_instance(instance, event, request.include)

        return m.UpdateResponse(instance=result)

    async def delete(
        self, request: m.DeleteRequest, *, transaction: cm.Transaction | None = None
    ) -> m.DeleteResponse:
        """Delete instance."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            event = await persistence.events.get(
                where={"id": request.where["event_id"]}
            )
            if event is None:
                return m.DeleteResponse(instance=None)

            instance = self._find_instance(event, request.where["start"])
            if instance is None:
                return m.DeleteResponse(instance=None)

            event = await persistence.events.update(
                data={
                    "exclude": (event.exclude or set())
                    | {m.Exclusion(start=instance.start)}
                },
                where={"id": event.id},
                include=self._event_include(request.include),
            )
            if event is None:
                return m.DeleteResponse(instance=None)

            result = self._map_instance(instance, event, request.include)

        return m.DeleteResponse(instance=result)
