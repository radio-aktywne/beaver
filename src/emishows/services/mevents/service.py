from collections.abc import Generator
from contextlib import contextmanager
from uuid import UUID

from litestar.channels import ChannelsPlugin

from emishows.models.events import mevent as ev
from emishows.models.events.event import Event
from emishows.services.datashows import errors as dse
from emishows.services.datashows import models as dsm
from emishows.services.datashows.service import DatashowsService
from emishows.services.datatimes import errors as dte
from emishows.services.datatimes import models as dtm
from emishows.services.datatimes.service import DatatimesService
from emishows.services.mevents import errors as e
from emishows.services.mevents import models as m
from emishows.services.shows import models as sm


class EventsService:
    """Service to manage events."""

    def __init__(
        self,
        datashows: DatashowsService,
        datatimes: DatatimesService,
        channels: ChannelsPlugin,
    ) -> None:
        self._datashows = datashows
        self._datatimes = datatimes
        self._channels = channels

    def _emit_event(self, event: Event) -> None:
        data = event.model_dump_json(by_alias=True)
        self._channels.publish(data, "events")

    def _emit_event_created_event(self, event: m.Event) -> None:
        event = ev.Event.map(event)
        data = ev.EventCreatedEventData(
            event=event,
        )
        event = ev.EventCreatedEvent(
            data=data,
        )
        self._emit_event(event)

    def _emit_event_updated_event(self, event: m.Event) -> None:
        event = ev.Event.map(event)
        data = ev.EventUpdatedEventData(
            event=event,
        )
        event = ev.EventUpdatedEvent(
            data=data,
        )
        self._emit_event(event)

    def _emit_event_deleted_event(self, event: m.Event) -> None:
        event = ev.Event.map(event)
        data = ev.EventDeletedEventData(
            event=event,
        )
        event = ev.EventDeletedEvent(
            data=data,
        )
        self._emit_event(event)

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except dse.DataError as ex:
            raise e.ValidationError(str(ex)) from ex
        except dse.ServiceError as ex:
            raise e.DatashowsError(str(ex)) from ex
        except dte.ServiceError as ex:
            raise e.DatatimesError(str(ex)) from ex

    async def _where_with_query(
        self, where: m.EventWhereInput | None, query: m.Query | None
    ) -> m.EventWhereInput | None:
        if query is None:
            return where

        req = dtm.QueryEventsRequest(
            query=query,
        )

        with self._handle_errors():
            res = await self._datatimes.query_events(req)

        events = res.events

        where = where.copy() if where is not None else {}
        filter = {
            "id": {
                "in": [str(event.id) for event in events],
            },
        }

        if "AND" in where:
            where["AND"].append(filter)
        else:
            where["AND"] = [filter]

        return where

    async def _map_event(self, dsevent: dsm.Event) -> m.Event:
        req = dtm.GetEventRequest(
            id=UUID(dsevent.id),
        )

        with self._handle_errors():
            res = await self._datatimes.get_event(req)

        if dsevent.show is not None:
            show = await self._map_show(dsevent.show)
        else:
            show = None

        return m.Event.merge(dsevent, res.event, show)

    async def _map_show(self, dsshow: dsm.Show) -> sm.Show:
        if dsshow.events is not None:
            events = [await self._map_event(event) for event in dsshow.events]
        else:
            events = None

        return sm.Show.map(dsshow, events)

    async def _merge_event(self, dsevent: dsm.Event, dtevent: dtm.Event) -> m.Event:
        if dsevent.show is not None:
            show = await self._map_show(dsevent.show)
        else:
            show = None

        return m.Event.merge(dsevent, dtevent, show)

    async def count(self, request: m.CountRequest) -> m.CountResponse:
        """Count events."""

        where = request.where
        query = request.query

        where = await self._where_with_query(where, query)

        with self._handle_errors():
            count = await self._datashows.event.count(
                where=where,
            )

        return m.CountResponse(
            count=count,
        )

    async def _list_datashows_events(
        self,
        limit: int | None,
        offset: int | None,
        where: m.EventWhereInput | None,
        include: m.EventInclude | None,
        order: m.EventOrderByInput | list[m.EventOrderByInput] | None,
    ) -> list[dsm.Event]:
        with self._handle_errors():
            return await self._datashows.event.find_many(
                take=limit,
                skip=offset,
                where=where,
                include=include,
                order=order,
            )

    async def _list_datatimes_events(
        self, dsevents: list[dsm.Event]
    ) -> list[dtm.Event]:
        dtevents = []

        for dsevent in dsevents:
            req = dtm.GetEventRequest(
                id=UUID(dsevent.id),
            )

            with self._handle_errors():
                res = await self._datatimes.get_event(req)

            dtevent = res.event
            dtevents.append(dtevent)

        return dtevents

    async def _list_sort_events(
        self,
        events: list[m.Event],
        order: m.EventOrderByInput | list[m.EventOrderByInput] | None,
    ) -> list[m.Event]:
        if order is None:
            return events

        if not isinstance(order, list):
            order = [order]

        for key, direction in reversed(order):
            events = sorted(
                events,
                key=lambda event: getattr(event, key),
                reverse=direction == "desc",
            )

        return events

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List all events."""

        limit = request.limit
        offset = request.offset
        where = request.where
        query = request.query
        include = request.include
        order = request.order

        where = await self._where_with_query(where, query)

        dsevents = await self._list_datashows_events(
            limit, offset, where, include, order
        )
        dtevents = await self._list_datatimes_events(dsevents)

        events = [
            await self._merge_event(dsevent, dtevent)
            for dsevent, dtevent in zip(dsevents, dtevents)
        ]
        events = await self._list_sort_events(events, order)

        return m.ListResponse(
            events=events,
        )

    async def _get_datashows_event(
        self, where: m.EventWhereUniqueInput, include: m.EventInclude | None
    ) -> dsm.Event | None:
        with self._handle_errors():
            return await self._datashows.event.find_unique(
                where=where,
                include=include,
            )

    async def _get_datatimes_event(self, dsevent: dsm.Event) -> dtm.Event:
        req = dtm.GetEventRequest(
            id=UUID(dsevent.id),
        )

        with self._handle_errors():
            res = await self._datatimes.get_event(req)

        return res.event

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get event."""

        where = request.where
        include = request.include

        dsevent = await self._get_datashows_event(where, include)

        if dsevent is None:
            return m.GetResponse(
                event=None,
            )

        dtevent = await self._get_datatimes_event(dsevent)

        event = await self._merge_event(dsevent, dtevent)

        return m.GetResponse(
            event=event,
        )

    async def _create_datashows_event(
        self,
        data: m.EventCreateInput,
        include: m.EventInclude | None,
        transaction: DatashowsService,
    ) -> dsm.Event:
        d = {"type": data["type"]}
        if "id" in data:
            d["id"] = data["id"]
        if "showId" in data:
            d["showId"] = data["showId"]

        with self._handle_errors():
            return await transaction.event.create(
                data=d,
                include=include,
            )

    async def _create_datatimes_event(
        self, data: m.EventCreateInput, dsevent: dsm.Event
    ) -> dtm.Event:
        dtevent = dtm.Event(
            id=UUID(dsevent.id),
            start=data["start"],
            end=data["end"],
            timezone=data["timezone"],
            recurrence=data.get("recurrence"),
        )
        req = dtm.UpsertEventRequest(
            event=dtevent,
        )

        with self._handle_errors():
            res = await self._datatimes.upsert_event(req)

        return res.event

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create event."""

        data = request.data
        include = request.include

        async with self._datashows.tx() as transaction:
            dsevent = await self._create_datashows_event(data, include, transaction)
            dtevent = await self._create_datatimes_event(data, dsevent)

        event = await self._merge_event(dsevent, dtevent)

        self._emit_event_created_event(event)

        return m.CreateResponse(
            event=event,
        )

    async def _update_datashows_event(
        self,
        data: m.EventUpdateInput,
        where: m.EventWhereUniqueInput,
        include: m.EventInclude | None,
        transaction: DatashowsService,
    ) -> dsm.Event | None:
        d = {}
        if "id" in data:
            d["id"] = data["id"]
        if "type" in data:
            d["type"] = data["type"]

        with self._handle_errors():
            return await transaction.event.update(
                data=d,
                where=where,
                include=include,
            )

    async def _update_datatimes_event(
        self, data: m.EventUpdateInput, odsevent: dsm.Event, ndsevent: dsm.Event
    ) -> dtm.Event:
        with self._handle_errors():
            req = dtm.GetEventRequest(
                id=UUID(odsevent.id),
            )

            res = await self._datatimes.get_event(req)

            odtevent = res.event

        ndtevent = dtm.Event(
            id=UUID(ndsevent.id),
            start=data.get("start", odtevent.start),
            end=data.get("end", odtevent.end),
            timezone=data.get("timezone", odtevent.timezone),
            recurrence=data.get("recurrence", odtevent.recurrence),
        )

        if odtevent.id != ndtevent.id:
            req = dtm.DeleteEventRequest(
                id=odtevent.id,
            )

            with self._handle_errors():
                await self._datatimes.delete_event(req)

        req = dtm.UpsertEventRequest(
            event=ndtevent,
        )

        with self._handle_errors():
            res = await self._datatimes.upsert_event(req)

        return res.event

    async def update(self, request: m.UpdateRequest) -> m.UpdateResponse:
        """Update event."""

        data = request.data
        where = request.where
        include = request.include

        async with self._datashows.tx() as transaction:
            odsevent = await self._get_datashows_event(where, None)

            ndsevent = await self._update_datashows_event(
                data, where, include, transaction
            )

            if ndsevent is None:
                return m.UpdateResponse(
                    event=None,
                )

            dtevent = await self._update_datatimes_event(data, odsevent, ndsevent)

        event = await self._merge_event(ndsevent, dtevent)

        self._emit_event_updated_event(event)

        return m.UpdateResponse(
            event=event,
        )

    async def _delete_datashows_event(
        self,
        where: m.EventWhereUniqueInput,
        include: m.EventInclude | None,
        transaction: DatashowsService,
    ) -> dsm.Event | None:
        with self._handle_errors():
            return await transaction.event.delete(
                where=where,
                include=include,
            )

    async def _delete_datatimes_event(self, dsevent: dsm.Event) -> dtm.Event:
        req = dtm.GetEventRequest(
            id=UUID(dsevent.id),
        )

        with self._handle_errors():
            res = await self._datatimes.get_event(req)

        dtevent = res.event

        req = dtm.DeleteEventRequest(
            id=dtevent.id,
        )

        with self._handle_errors():
            await self._datatimes.delete_event(req)

        return dtevent

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete event."""

        where = request.where
        include = request.include

        async with self._datashows.tx() as transaction:
            dsevent = await self._delete_datashows_event(where, include, transaction)

            if dsevent is None:
                return m.DeleteResponse(
                    event=None,
                )

            dtevent = await self._delete_datatimes_event(dsevent)

        event = await self._merge_event(dsevent, dtevent)

        self._emit_event_deleted_event(event)

        return m.DeleteResponse(
            event=event,
        )
