from collections.abc import Generator, Sequence
from contextlib import contextmanager
from typing import cast
from uuid import UUID

from litestar.channels import ChannelsPlugin

from beaver.models.events import mevent as ev
from beaver.models.events.event import Event
from beaver.services.howlite import errors as hle
from beaver.services.howlite import models as hlm
from beaver.services.howlite.service import HowliteService
from beaver.services.mevents import errors as e
from beaver.services.mevents import models as m
from beaver.services.sapphire import errors as spe
from beaver.services.sapphire import models as spm
from beaver.services.sapphire import types as spt
from beaver.services.sapphire.service import SapphireService


class EventsService:
    """Service to manage events."""

    def __init__(
        self,
        howlite: HowliteService,
        sapphire: SapphireService,
        channels: ChannelsPlugin,
    ) -> None:
        self._howlite = howlite
        self._sapphire = sapphire
        self._channels = channels

    def _emit_event(self, event: Event) -> None:
        data = event.model_dump_json(by_alias=True)
        self._channels.publish(data, "events")

    def _emit_event_created_event(self, event: m.Event) -> None:
        mapped_event = ev.Event.map(event)
        created_event_data = ev.EventCreatedEventData(
            event=mapped_event,
        )
        created_event = ev.EventCreatedEvent(
            data=created_event_data,
        )
        self._emit_event(created_event)

    def _emit_event_updated_event(self, event: m.Event) -> None:
        mapped_event = ev.Event.map(event)
        updated_event_data = ev.EventUpdatedEventData(
            event=mapped_event,
        )
        updated_event = ev.EventUpdatedEvent(
            data=updated_event_data,
        )
        self._emit_event(updated_event)

    def _emit_event_deleted_event(self, event: m.Event) -> None:
        mapped_event = ev.Event.map(event)
        deleted_event_data = ev.EventDeletedEventData(
            event=mapped_event,
        )
        deleted_event = ev.EventDeletedEvent(
            data=deleted_event_data,
        )
        self._emit_event(deleted_event)

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except hle.ServiceError as ex:
            raise e.HowliteError(str(ex)) from ex
        except spe.DataError as ex:
            raise e.ValidationError(str(ex)) from ex
        except spe.ServiceError as ex:
            raise e.SapphireError(str(ex)) from ex

    async def _where_with_query(
        self, where: m.EventWhereInput | None, query: m.Query | None
    ) -> m.EventWhereInput | None:
        if query is None:
            return where

        req = hlm.QueryEventsRequest(
            query=query,
        )

        with self._handle_errors():
            res = await self._howlite.query_events(req)

        events = res.events

        where = where.copy() if where is not None else {}
        extra_where: m.EventWhereInput = {
            "id": {
                "in": [str(event.id) for event in events],
            },
        }

        if "AND" in where:
            where["AND"].append(extra_where)
        else:
            where["AND"] = [extra_where]

        return where

    async def _map_event(self, dsevent: spm.Event) -> m.Event:
        req = hlm.GetEventRequest(
            id=UUID(dsevent.id),
        )

        with self._handle_errors():
            res = await self._howlite.get_event(req)

        if dsevent.show is not None:
            show = await self._map_show(dsevent.show)
        else:
            show = None

        return m.Event.merge(dsevent, res.event, show)

    async def _map_show(self, dsshow: spm.Show) -> m.Show:
        if dsshow.events is not None:
            events = [await self._map_event(event) for event in dsshow.events]
        else:
            events = None

        return m.Show.map(dsshow, events)

    async def _merge_event(self, dsevent: spm.Event, dtevent: hlm.Event) -> m.Event:
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
            count = await self._sapphire.event.count(
                where=where,
            )

        return m.CountResponse(
            count=count,
        )

    async def _list_sapphire_events(
        self,
        limit: int | None,
        offset: int | None,
        where: m.EventWhereInput | None,
        include: m.EventInclude | None,
        order: m.EventOrderByInput | Sequence[m.EventOrderByInput] | None,
    ) -> Sequence[spm.Event]:
        with self._handle_errors():
            return await self._sapphire.event.find_many(
                take=limit,
                skip=offset,
                where=where,
                include=include,
                order=cast("list[spt.EventOrderByInput]", list(order))
                if isinstance(order, Sequence)
                else cast("spt.EventOrderByInput | None", order),
            )

    async def _list_howlite_events(
        self, dsevents: Sequence[spm.Event]
    ) -> Sequence[hlm.Event]:
        dtevents = []

        for dsevent in dsevents:
            req = hlm.GetEventRequest(
                id=UUID(dsevent.id),
            )

            with self._handle_errors():
                res = await self._howlite.get_event(req)

            dtevent = res.event
            dtevents.append(dtevent)

        return dtevents

    async def _list_sort_events(
        self,
        events: Sequence[m.Event],
        order: m.EventOrderByInput | Sequence[m.EventOrderByInput] | None,
    ) -> Sequence[m.Event]:
        if order is None:
            return list(events)

        if not isinstance(order, Sequence):
            order = [order]

        for key, direction in reversed(order):
            events = sorted(
                events,
                key=lambda event: getattr(event, key),
                reverse=direction == "desc",
            )

        return list(events)

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List all events."""
        limit = request.limit
        offset = request.offset
        where = request.where
        query = request.query
        include = request.include
        order = request.order

        where = await self._where_with_query(where, query)

        dsevents = await self._list_sapphire_events(
            limit, offset, where, include, order
        )
        dtevents = await self._list_howlite_events(dsevents)

        events = [
            await self._merge_event(dsevent, dtevent)
            for dsevent, dtevent in zip(dsevents, dtevents, strict=False)
        ]
        events = await self._list_sort_events(events, order)

        return m.ListResponse(
            events=events,
        )

    async def _get_sapphire_event(
        self, where: m.EventWhereUniqueInput, include: m.EventInclude | None
    ) -> spm.Event | None:
        with self._handle_errors():
            return await self._sapphire.event.find_unique(
                where=where,
                include=include,
            )

    async def _get_howlite_event(self, dsevent: spm.Event) -> hlm.Event:
        req = hlm.GetEventRequest(
            id=UUID(dsevent.id),
        )

        with self._handle_errors():
            res = await self._howlite.get_event(req)

        return res.event

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get event."""
        where = request.where
        include = request.include

        dsevent = await self._get_sapphire_event(where, include)

        if dsevent is None:
            return m.GetResponse(
                event=None,
            )

        dtevent = await self._get_howlite_event(dsevent)

        event = await self._merge_event(dsevent, dtevent)

        return m.GetResponse(
            event=event,
        )

    async def _create_sapphire_event(
        self,
        data: m.EventCreateInput,
        include: m.EventInclude | None,
        transaction: SapphireService,
    ) -> spm.Event:
        d: spt.EventCreateInput = {"type": data["type"]}
        if "id" in data:
            d["id"] = data["id"]
        if "showId" in data:
            d["showId"] = data["showId"]

        with self._handle_errors():
            return await transaction.event.create(
                data=d,
                include=include,
            )

    async def _create_howlite_event(
        self, data: m.EventCreateInput, dsevent: spm.Event
    ) -> hlm.Event:
        dtevent = hlm.Event(
            id=UUID(dsevent.id),
            start=data["start"],
            end=data["end"],
            timezone=data["timezone"],
            recurrence=data.get("recurrence"),
        )
        req = hlm.UpsertEventRequest(
            event=dtevent,
        )

        with self._handle_errors():
            res = await self._howlite.upsert_event(req)

        return res.event

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create event."""
        data = request.data
        include = request.include

        async with self._sapphire.tx() as transaction:
            dsevent = await self._create_sapphire_event(data, include, transaction)
            dtevent = await self._create_howlite_event(data, dsevent)

        event = await self._merge_event(dsevent, dtevent)

        self._emit_event_created_event(event)

        return m.CreateResponse(
            event=event,
        )

    async def _update_sapphire_event(
        self,
        data: m.EventUpdateInput,
        where: m.EventWhereUniqueInput,
        include: m.EventInclude | None,
        transaction: SapphireService,
    ) -> spm.Event | None:
        d: spt.EventUpdateInput = {}
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

    async def _update_howlite_event(
        self, data: m.EventUpdateInput, odsevent: spm.Event, ndsevent: spm.Event
    ) -> hlm.Event:
        with self._handle_errors():
            req = hlm.GetEventRequest(
                id=UUID(odsevent.id),
            )

            res = await self._howlite.get_event(req)

            odtevent = res.event

        ndtevent = hlm.Event(
            id=UUID(ndsevent.id),
            start=data.get("start", odtevent.start),
            end=data.get("end", odtevent.end),
            timezone=data.get("timezone", odtevent.timezone),
            recurrence=data.get("recurrence", odtevent.recurrence),
        )

        if odtevent.id != ndtevent.id:
            req = hlm.DeleteEventRequest(
                id=odtevent.id,
            )

            with self._handle_errors():
                await self._howlite.delete_event(req)

        req = hlm.UpsertEventRequest(
            event=ndtevent,
        )

        with self._handle_errors():
            res = await self._howlite.upsert_event(req)

        return res.event

    async def update(self, request: m.UpdateRequest) -> m.UpdateResponse:
        """Update event."""
        data = request.data
        where = request.where
        include = request.include

        async with self._sapphire.tx() as transaction:
            odsevent = await self._get_sapphire_event(where, None)

            ndsevent = await self._update_sapphire_event(
                data, where, include, transaction
            )

            if odsevent is None or ndsevent is None:
                return m.UpdateResponse(
                    event=None,
                )

            dtevent = await self._update_howlite_event(data, odsevent, ndsevent)

        event = await self._merge_event(ndsevent, dtevent)

        self._emit_event_updated_event(event)

        return m.UpdateResponse(
            event=event,
        )

    async def _delete_sapphire_event(
        self,
        where: m.EventWhereUniqueInput,
        include: m.EventInclude | None,
        transaction: SapphireService,
    ) -> spm.Event | None:
        with self._handle_errors():
            return await transaction.event.delete(
                where=where,
                include=include,
            )

    async def _delete_howlite_event(self, dsevent: spm.Event) -> hlm.Event:
        req = hlm.GetEventRequest(
            id=UUID(dsevent.id),
        )

        with self._handle_errors():
            res = await self._howlite.get_event(req)

        dtevent = res.event

        req = hlm.DeleteEventRequest(
            id=dtevent.id,
        )

        with self._handle_errors():
            await self._howlite.delete_event(req)

        return dtevent

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete event."""
        where = request.where
        include = request.include

        async with self._sapphire.tx() as transaction:
            dsevent = await self._delete_sapphire_event(where, include, transaction)

            if dsevent is None:
                return m.DeleteResponse(
                    event=None,
                )

            dtevent = await self._delete_howlite_event(dsevent)

        event = await self._merge_event(dsevent, dtevent)

        self._emit_event_deleted_event(event)

        return m.DeleteResponse(
            event=event,
        )
