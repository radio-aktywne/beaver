from collections.abc import Generator, Sequence
from contextlib import contextmanager, suppress
from dataclasses import replace
from uuid import UUID

from beaver.services.consistency.coordination import models as cm
from beaver.services.data.howlite import errors as he, models as hm
from beaver.services.data.sapphire import errors as se, models as sm, types as st
from beaver.services.persistence.events import errors as e, models as m
from beaver.services.persistence.reader import errors as re
from beaver.services.persistence.reader.service import RecordReader


class EventsPersistenceService:
    """Service to persist events across both stores."""

    def __init__(self, transaction: cm.Transaction) -> None:
        self._transaction = transaction
        self._reader = RecordReader(transaction.howlite)

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except se.UniqueViolationError as ex:
            raise e.ConflictError from ex
        except se.DataError as ex:
            raise e.ValidationError from ex
        except (
            he.ServiceError,
            se.ServiceError,
            re.ServiceError,
        ) as ex:
            raise e.ServiceError from ex

    async def _query(
        self, where: st.EventWhereInput | None, query: hm.Query | None
    ) -> st.EventWhereInput | None:
        if query is None:
            return where

        response = await self._transaction.howlite.query_events(
            hm.QueryEventsRequest(query=query)
        )

        candidates: st.EventWhereInput = {
            "id": {"in": [str(event.id) for event in response.events]}
        }

        return {"AND": [where, candidates]} if where is not None else candidates

    async def _get_howlite(self, event_id: str) -> hm.Event:
        try:
            response = await self._transaction.howlite.get_event(
                hm.GetEventRequest(id=UUID(event_id))
            )
        except he.NotFoundError as ex:
            raise e.MissingHowliteEventError(event_id) from ex

        return response.event

    async def _get_show(self, sevent: sm.Event) -> sm.Show | None:
        if sevent.show is not None:
            return sevent.show

        if sevent.showId is None:
            return None

        return await self._transaction.sapphire.show.find_unique(
            where={"id": sevent.showId}
        )

    async def _create_howlite(self, data: m.EventCreateInput, sevent: sm.Event) -> None:
        sshow = await self._get_show(sevent)

        hevent = hm.Event(
            id=UUID(sevent.id),
            summary=sshow.title if sshow is not None else None,
            description=sshow.description if sshow is not None else None,
            categories={str(sevent.type)},
            start=data["start"],
            duration=data["duration"],
            timezone=data["timezone"],
            recurrence=data.get("recurrence"),
            include=data.get("include"),
            exclude=data.get("exclude"),
        )

        await self._transaction.howlite.upsert_event(
            hm.UpsertEventRequest(event=hevent)
        )

    def _updated_recurrence(
        self, recurrence: hm.Recurrence | None, data: m.EventUpdateInput
    ) -> hm.Recurrence | None:
        if "recurrence" not in data:
            return recurrence

        update = data["recurrence"]
        if update is None:
            return None

        if recurrence is not None:
            return replace(recurrence, **update)

        if "frequency" not in update:
            raise e.PartialUpdateInsufficientDataError

        return hm.Recurrence(**update)

    async def _update_howlite(
        self,
        data: m.EventUpdateInput,
        sevent: sm.Event,
        old_hevent: hm.Event,
    ) -> None:
        sshow = await self._get_show(sevent)

        hevent = hm.Event(
            id=UUID(sevent.id),
            summary=sshow.title if sshow is not None else None,
            description=sshow.description if sshow is not None else None,
            categories={str(sevent.type)},
            start=data.get("start", old_hevent.start),
            duration=data.get("duration", old_hevent.duration),
            timezone=data.get("timezone", old_hevent.timezone),
            recurrence=self._updated_recurrence(old_hevent.recurrence, data),
            include=data.get("include", old_hevent.include),
            exclude=data.get("exclude", old_hevent.exclude),
        )

        if hevent != old_hevent:
            await self._transaction.howlite.upsert_event(
                hm.UpsertEventRequest(event=hevent)
            )

        if old_hevent.id != hevent.id:
            await self._delete_howlite(str(old_hevent.id))

    async def _delete_howlite(self, event_id: str) -> None:
        with suppress(he.NotFoundError):
            await self._transaction.howlite.delete_event(
                hm.DeleteEventRequest(id=UUID(event_id))
            )

    async def count(
        self,
        where: m.EventWhereInput | None = None,
        query: m.Query | None = None,
    ) -> int:
        """Count events matching the filters."""
        with self._handle_errors():
            return await self._transaction.sapphire.event.count(
                where=await self._query(where, query)
            )

    async def get(
        self,
        where: m.EventWhereUniqueInput,
        *,
        include: m.EventInclude | None = None,
    ) -> m.Event | None:
        """Read an event with its requested relations."""
        with self._handle_errors():
            sevent = await self._transaction.sapphire.event.find_unique(
                where=where, include=include
            )

            return await self._reader.read_event(sevent) if sevent is not None else None

    async def list(
        self,
        *,
        where: m.EventWhereInput | None = None,
        query: m.Query | None = None,
        include: m.EventInclude | None = None,
        take: int | None = None,
        skip: int | None = None,
        order: m.EventOrderByInput | Sequence[m.EventOrderByInput] | None = None,
    ) -> Sequence[m.Event]:
        """Read a page of events and their requested relations."""
        with self._handle_errors():
            if take == 0:
                return []

            sevents = await self._transaction.sapphire.event.find_many(
                where=await self._query(where, query),
                include=include,
                take=take,
                skip=skip,
                order=list(order) if isinstance(order, Sequence) else order,
            )

            return [await self._reader.read_event(sevent) for sevent in sevents]

    async def create(
        self,
        data: m.EventCreateInput,
        *,
        include: m.EventInclude | None = None,
    ) -> m.Event:
        """Create both representations of an event."""
        with self._handle_errors():
            sdata: st.EventCreateInput = {"type": data["type"]}
            if "id" in data:
                sdata["id"] = data["id"]
            if "showId" in data:
                sdata["showId"] = data["showId"]

            sevent = await self._transaction.sapphire.event.create(
                data=sdata, include=include
            )

            await self._create_howlite(data, sevent)

            return await self._reader.read_event(sevent)

    async def update(
        self,
        data: m.EventUpdateInput,
        *,
        where: m.EventWhereUniqueInput,
        include: m.EventInclude | None = None,
    ) -> m.Event | None:
        """Update both representations of an event."""
        with self._handle_errors():
            if not data:
                return await self.get(where, include=include)

            sevent = await self._transaction.sapphire.event.find_unique(where=where)

            if sevent is None:
                return None

            hevent = await self._get_howlite(sevent.id)

            sdata: st.EventUpdateInput = {}
            if "id" in data:
                sdata["id"] = data["id"]
            if "type" in data:
                sdata["type"] = data["type"]

            sevent = await self._transaction.sapphire.event.update(
                data=sdata, where=where, include=include
            )

            if sevent is None:
                return None

            await self._update_howlite(data, sevent, hevent)

            return await self._reader.read_event(sevent)

    async def delete(
        self,
        where: m.EventWhereUniqueInput,
        *,
        include: m.EventInclude | None = None,
    ) -> m.Event | None:
        """Delete both representations and return the event's previous data."""
        with self._handle_errors():
            sevent = await self._transaction.sapphire.event.find_unique(
                where=where, include=include
            )

            if sevent is None:
                return None

            event = await self._reader.read_event(sevent)

            await self._delete_howlite(sevent.id)
            await self._transaction.sapphire.event.delete(where={"id": sevent.id})

            return event
