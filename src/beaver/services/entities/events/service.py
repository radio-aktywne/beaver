from collections.abc import Generator, Sequence
from contextlib import contextmanager
from typing import cast
from uuid import UUID

from beaver.services.data.howlite import errors as he
from beaver.services.data.howlite import models as hm
from beaver.services.data.howlite.service import HowliteService
from beaver.services.data.sapphire import errors as se
from beaver.services.data.sapphire import models as sm
from beaver.services.data.sapphire import types as st
from beaver.services.data.sapphire.service import SapphireService
from beaver.services.entities.events import errors as e
from beaver.services.entities.events import models as m


class EventsService:
    """Service to manage events."""

    def __init__(self, howlite: HowliteService, sapphire: SapphireService) -> None:
        self._howlite = howlite
        self._sapphire = sapphire

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except se.DataError as ex:
            raise e.ValidationError from ex
        except (he.ServiceError, se.ServiceError) as ex:
            raise e.ServiceError from ex

    async def _where_with_query(
        self, where: m.EventWhereInput | None, query: m.Query | None
    ) -> m.EventWhereInput | None:
        if query is None:
            return where

        request = hm.QueryEventsRequest(query=query)

        with self._handle_errors():
            response = await self._howlite.query_events(request)

        where = where.copy() if where is not None else {}
        extra_where: m.EventWhereInput = {
            "id": {
                "in": [str(event.id) for event in response.events],
            },
        }

        if "AND" in where:
            where["AND"].append(extra_where)
        else:
            where["AND"] = [extra_where]

        return where

    async def _merge_event(self, sevent: sm.Event, hevent: hm.Event) -> m.Event:
        if sevent.show is not None:
            show = await self._map_show(sevent.show)
        else:
            show = None

        return m.Event.map(sevent, hevent, show)

    async def _map_event(self, sevent: sm.Event) -> m.Event:
        request = hm.GetEventRequest(id=UUID(sevent.id))

        with self._handle_errors():
            response = await self._howlite.get_event(request)

        return await self._merge_event(sevent, response.event)

    async def _map_show(self, sshow: sm.Show) -> m.Show:
        if sshow.events is not None:
            events = [await self._map_event(event) for event in sshow.events]
        else:
            events = None

        return m.Show.map(sshow, events)

    async def count(self, request: m.CountRequest) -> m.CountResponse:
        """Count events."""
        where = await self._where_with_query(request.where, request.query)

        with self._handle_errors():
            count = await self._sapphire.event.count(where=where)

        return m.CountResponse(count=count)

    async def _list_sapphire_events(
        self,
        limit: int | None,
        offset: int | None,
        where: m.EventWhereInput | None,
        include: m.EventInclude | None,
        order: m.EventOrderByInput | Sequence[m.EventOrderByInput] | None,
    ) -> Sequence[sm.Event]:
        with self._handle_errors():
            return await self._sapphire.event.find_many(
                take=limit,
                skip=offset,
                where=where,
                include=include,
                order=cast("list[st.EventOrderByInput]", list(order))
                if isinstance(order, Sequence)
                else cast("st.EventOrderByInput | None", order),
            )

    async def _list_howlite_events(
        self, sevents: Sequence[sm.Event]
    ) -> Sequence[hm.Event]:
        hevents = []

        for sevent in sevents:
            request = hm.GetEventRequest(id=UUID(sevent.id))

            with self._handle_errors():
                response = await self._howlite.get_event(request)

            hevent = response.event
            hevents.append(hevent)

        return hevents

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
        """List events."""
        where = await self._where_with_query(request.where, request.query)

        sevents = await self._list_sapphire_events(
            request.limit, request.offset, where, request.include, request.order
        )
        hevents = await self._list_howlite_events(sevents)

        events = [
            await self._merge_event(dsevent, dtevent)
            for dsevent, dtevent in zip(sevents, hevents, strict=False)
        ]
        events = await self._list_sort_events(events, request.order)

        return m.ListResponse(events=events)

    async def _get_sapphire_event(
        self, where: m.EventWhereUniqueInput, include: m.EventInclude | None
    ) -> sm.Event | None:
        with self._handle_errors():
            return await self._sapphire.event.find_unique(where=where, include=include)

    async def _get_howlite_event(self, sevent: sm.Event) -> hm.Event:
        request = hm.GetEventRequest(id=UUID(sevent.id))

        with self._handle_errors():
            response = await self._howlite.get_event(request)

        return response.event

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get event."""
        sevent = await self._get_sapphire_event(request.where, request.include)

        if sevent is None:
            return m.GetResponse(event=None)

        hevent = await self._get_howlite_event(sevent)
        event = await self._merge_event(sevent, hevent)

        return m.GetResponse(event=event)

    async def _create_sapphire_event(
        self,
        data: m.EventCreateInput,
        include: m.EventInclude | None,
        transaction: SapphireService,
    ) -> sm.Event:
        d: st.EventCreateInput = {"type": data["type"]}
        if "id" in data:
            d["id"] = data["id"]
        if "showId" in data:
            d["showId"] = data["showId"]

        with self._handle_errors():
            return await transaction.event.create(data=d, include=include)

    async def _create_howlite_event(
        self, data: m.EventCreateInput, sevent: sm.Event
    ) -> hm.Event:
        hevent = hm.Event(
            id=UUID(sevent.id),
            start=data["start"],
            duration=data["duration"],
            timezone=data["timezone"],
            recurrence=data.get("recurrence"),
        )
        request = hm.UpsertEventRequest(event=hevent)

        with self._handle_errors():
            response = await self._howlite.upsert_event(request)

        return response.event

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create event."""
        async with self._sapphire.tx() as transaction:
            sevent = await self._create_sapphire_event(
                request.data, request.include, transaction
            )
            hevent = await self._create_howlite_event(request.data, sevent)

        event = await self._merge_event(sevent, hevent)
        return m.CreateResponse(event=event)

    async def _update_sapphire_event(
        self,
        data: m.EventUpdateInput,
        where: m.EventWhereUniqueInput,
        include: m.EventInclude | None,
        transaction: SapphireService,
    ) -> sm.Event | None:
        d: st.EventUpdateInput = {}
        if "id" in data:
            d["id"] = data["id"]
        if "type" in data:
            d["type"] = data["type"]

        with self._handle_errors():
            return await transaction.event.update(data=d, where=where, include=include)

    async def _update_howlite_event(
        self, data: m.EventUpdateInput, osevent: sm.Event, nsevent: sm.Event
    ) -> hm.Event:
        with self._handle_errors():
            request = hm.GetEventRequest(id=UUID(osevent.id))
            response = await self._howlite.get_event(request)
            ohevent = response.event

        if "recurrence" not in data:
            recurrence = ohevent.recurrence
        elif data["recurrence"] is None:
            recurrence = None
        elif ohevent.recurrence is not None:
            orr = ohevent.recurrence.rule
            recurrence = hm.Recurrence(
                rule=hm.RecurrenceRule(
                    frequency=rule.get("frequency", orr.frequency),
                    until=rule.get("until", orr.until),
                    count=rule.get("count", orr.count),
                    interval=rule.get("interval", orr.interval),
                    by_seconds=rule.get("by_seconds", orr.by_seconds),
                    by_minutes=rule.get("by_minutes", orr.by_minutes),
                    by_hours=rule.get("by_hours", orr.by_hours),
                    by_weekdays=rule.get("by_weekdays", orr.by_weekdays),
                    by_monthdays=rule.get("by_monthdays", orr.by_monthdays),
                    by_yeardays=rule.get("by_yeardays", orr.by_yeardays),
                    by_weeks=rule.get("by_weeks", orr.by_weeks),
                    by_months=rule.get("by_months", orr.by_months),
                    by_set_positions=rule.get("by_set_positions", orr.by_set_positions),
                    week_start=rule.get("week_start", orr.week_start),
                )
                if "rule" in data["recurrence"] and (rule := data["recurrence"]["rule"])
                else orr,
                include=data["recurrence"].get("include", ohevent.recurrence.include),
                exclude=data["recurrence"].get("exclude", ohevent.recurrence.exclude),
            )
        else:
            if "rule" not in data["recurrence"]:
                raise e.PartialUpdateInsufficientDataError

            rule = data["recurrence"]["rule"]

            if "frequency" not in rule:
                raise e.PartialUpdateInsufficientDataError

            recurrence = hm.Recurrence(
                rule=hm.RecurrenceRule(
                    frequency=rule["frequency"],
                    until=rule.get("until"),
                    count=rule.get("count"),
                    interval=rule.get("interval"),
                    by_seconds=rule.get("by_seconds"),
                    by_minutes=rule.get("by_minutes"),
                    by_hours=rule.get("by_hours"),
                    by_weekdays=rule.get("by_weekdays"),
                    by_monthdays=rule.get("by_monthdays"),
                    by_yeardays=rule.get("by_yeardays"),
                    by_weeks=rule.get("by_weeks"),
                    by_months=rule.get("by_months"),
                    by_set_positions=rule.get("by_set_positions"),
                    week_start=rule.get("week_start"),
                ),
                include=data["recurrence"].get("include"),
                exclude=data["recurrence"].get("exclude"),
            )

        nhevent = hm.Event(
            id=UUID(nsevent.id),
            start=data.get("start", ohevent.start),
            duration=data.get("duration", ohevent.duration),
            timezone=data.get("timezone", ohevent.timezone),
            recurrence=recurrence,
        )

        if ohevent.id != nhevent.id:
            request = hm.DeleteEventRequest(id=ohevent.id)

            with self._handle_errors():
                await self._howlite.delete_event(request)

        request = hm.UpsertEventRequest(event=nhevent)

        with self._handle_errors():
            response = await self._howlite.upsert_event(request)

        return response.event

    async def update(self, request: m.UpdateRequest) -> m.UpdateResponse:
        """Update event."""
        async with self._sapphire.tx() as transaction:
            osevent = await self._get_sapphire_event(request.where, None)
            nsevent = await self._update_sapphire_event(
                request.data, request.where, request.include, transaction
            )

            if osevent is None or nsevent is None:
                return m.UpdateResponse(event=None)

            hevent = await self._update_howlite_event(request.data, osevent, nsevent)

        event = await self._merge_event(nsevent, hevent)
        return m.UpdateResponse(event=event)

    async def _delete_sapphire_event(
        self,
        where: m.EventWhereUniqueInput,
        include: m.EventInclude | None,
        transaction: SapphireService,
    ) -> sm.Event | None:
        with self._handle_errors():
            return await transaction.event.delete(where=where, include=include)

    async def _delete_howlite_event(self, dsevent: sm.Event) -> hm.Event:
        get_event_request = hm.GetEventRequest(id=UUID(dsevent.id))

        with self._handle_errors():
            get_event_response = await self._howlite.get_event(get_event_request)

        hevent = get_event_response.event
        delete_event_request = hm.DeleteEventRequest(id=hevent.id)

        with self._handle_errors():
            await self._howlite.delete_event(delete_event_request)

        return hevent

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete event."""
        async with self._sapphire.tx() as transaction:
            sevent = await self._delete_sapphire_event(
                request.where, request.include, transaction
            )

            if sevent is None:
                return m.DeleteResponse(event=None)

            hevent = await self._delete_howlite_event(sevent)

        event = await self._merge_event(sevent, hevent)
        return m.DeleteResponse(event=event)
