from uuid import UUID

from litestar.channels import ChannelsPlugin
from prisma import Prisma
from prisma import errors as pe
from pydantic import NaiveDatetime, TypeAdapter

from emishows.emitimes import errors as te
from emishows.emitimes import models as tm
from emishows.emitimes.service import EmitimesService
from emishows.events import errors as ee
from emishows.events import models as em
from emishows.models import events as ev
from emishows.time import Timezone


class EventsService:
    """Service to manage events."""

    def __init__(
        self, prisma: Prisma, emitimes: EmitimesService, channels: ChannelsPlugin
    ) -> None:
        self._prisma = prisma
        self._emitimes = emitimes
        self._channels = channels

    def _emit_event(self, event: ev.Event) -> None:
        """Emit an event."""

        data = event.model_dump_json(by_alias=True)
        self._channels.publish(data, "events")

    def _normalize_event(self, event: em.Event) -> em.Event:
        """Normalize a show."""

        return em.Event(
            id=event.id,
            type=event.type,
            showId=event.showId,
            start=event.start,
            end=event.end,
            timezone=event.timezone,
            recurrence=event.recurrence,
        )

    def _emit_event_created_event(self, event: em.Event) -> None:
        """Emit a event created event."""

        event = self._normalize_event(event)
        event = ev.EventCreatedEvent(data=ev.EventCreatedEventData(event=event))
        self._emit_event(event)

    def _emit_event_updated_event(self, event: em.Event) -> None:
        """Emit a event updated event."""

        event = self._normalize_event(event)
        event = ev.EventUpdatedEvent(data=ev.EventUpdatedEventData(event=event))
        self._emit_event(event)

    def _emit_event_deleted_event(self, event: em.Event) -> None:
        """Emit a event deleted event."""

        event = self._normalize_event(event)
        event = ev.EventDeletedEvent(data=ev.EventDeletedEventData(event=event))
        self._emit_event(event)

    def _merge_events(
        self,
        database: em.EventDatabaseModel,
        emitimes: tm.Event,
    ) -> em.Event:
        """Merge database and emitimes events."""

        return em.Event(
            id=database.id,
            type=database.type,
            showId=database.showId,
            show=database.show,
            start=emitimes.start,
            end=emitimes.end,
            timezone=emitimes.timezone,
            recurrence=emitimes.recurrence,
        )

    async def count(
        self,
        request: em.CountRequest,
    ) -> em.CountResponse:
        """Count events."""

        where = request.where

        if request.query:
            try:
                events = await self._emitimes.query_events(
                    query=request.query,
                )
            except te.EmitimesError as e:
                raise ee.EmitimesError(str(e)) from e

            where = where.copy() if where else {}
            ids = [str(event.id) for event in events]
            filter = {"id": {"in": ids}}

            if "AND" in where:
                where["AND"].append(filter)
            else:
                where["AND"] = [filter]

        try:
            count = await self._prisma.event.count(
                where=where,
            )
        except pe.DataError as e:
            raise ee.ValidationError(str(e)) from e
        except pe.PrismaError as e:
            raise ee.DatabaseError(str(e)) from e

        return em.CountResponse(count=count)

    async def list(
        self,
        request: em.ListRequest,
    ) -> em.ListResponse:
        """List all events."""

        where = request.where

        if request.query:
            try:
                events = await self._emitimes.query_events(
                    query=request.query,
                )
            except te.EmitimesError as e:
                raise ee.EmitimesError(str(e)) from e

            where = where.copy() if where else {}
            ids = [str(event.id) for event in events]
            filter = {"id": {"in": ids}}

            if "AND" in where:
                where["AND"].append(filter)
            else:
                where["AND"] = [filter]

        try:
            database_events = await self._prisma.event.find_many(
                take=request.limit,
                skip=request.offset,
                where=where,
                include=request.include,
                order=request.order,
            )
        except pe.DataError as e:
            raise ee.ValidationError(str(e)) from e
        except pe.PrismaError as e:
            raise ee.DatabaseError(str(e)) from e

        events = []

        for database_event in database_events:
            try:
                emitimes_event = await self._emitimes.get_event(
                    id=UUID(database_event.id),
                )
            except te.EmitimesError as e:
                raise ee.EmitimesError(str(e)) from e

            event = self._merge_events(database_event, emitimes_event)
            events.append(event)

        order = request.order
        if order is not None:
            if not isinstance(order, list):
                order = [order]

            order = [
                (key, direction)
                for ordering in order
                for key, direction in ordering.items()
            ]

            for key, direction in reversed(order):
                events = sorted(
                    events,
                    key=lambda event: getattr(event, key),
                    reverse=direction == "desc",
                )

        return em.ListResponse(events=events)

    async def get(
        self,
        request: em.GetRequest,
    ) -> em.GetResponse:
        """Get an event."""

        try:
            database_event = await self._prisma.event.find_unique(
                where=request.where,
                include=request.include,
            )
        except pe.DataError as e:
            raise ee.ValidationError(str(e)) from e
        except pe.PrismaError as e:
            raise ee.DatabaseError(str(e)) from e

        if database_event is None:
            return em.GetResponse(event=None)

        try:
            emitimes_event = await self._emitimes.get_event(
                id=UUID(database_event.id),
            )
        except te.EmitimesError as e:
            raise ee.EmitimesError(str(e)) from e

        event = self._merge_events(database_event, emitimes_event)
        return em.GetResponse(event=event)

    async def create(
        self,
        request: em.CreateRequest,
    ) -> em.CreateResponse:
        """Create an event."""

        async with self._prisma.tx() as transaction:
            try:
                data = {"type": request.data["type"]}
                if "id" in request.data:
                    data["id"] = request.data["id"]
                if "showId" in request.data:
                    data["showId"] = request.data["showId"]
                if "show" in request.data:
                    data["show"] = request.data["show"]

                database_event = await transaction.event.create(
                    data=data,
                    include=request.include,
                )
            except pe.DataError as e:
                raise ee.ValidationError(str(e)) from e
            except pe.PrismaError as e:
                raise ee.DatabaseError(str(e)) from e

            try:
                data = tm.Event(
                    id=database_event.id,
                    start=request.data.get("start"),
                    end=request.data.get("end"),
                    timezone=request.data.get("timezone"),
                    recurrence=request.data.get("recurrence"),
                )
                emitimes_event = await self._emitimes.upsert_event(data)
            except te.EmitimesError as e:
                raise ee.EmitimesError(str(e)) from e

        event = self._merge_events(database_event, emitimes_event)

        self._emit_event_created_event(event)

        return em.CreateResponse(event=event)

    async def update(
        self,
        request: em.UpdateRequest,
    ) -> em.UpdateResponse:
        """Update an event."""

        async with self._prisma.tx() as transaction:
            try:
                data = {}
                if "id" in request.data:
                    data["id"] = request.data["id"]
                if "type" in request.data:
                    data["type"] = request.data["type"]
                if "show" in request.data:
                    data["show"] = request.data["show"]

                database_event = await transaction.event.update(
                    data=data,
                    where=request.where,
                    include=request.include,
                )
            except pe.DataError as e:
                raise ee.ValidationError(str(e)) from e
            except pe.PrismaError as e:
                raise ee.DatabaseError(str(e)) from e

            if database_event is None:
                return em.UpdateResponse(event=None)

            try:
                data = await self._emitimes.get_event(
                    id=UUID(database_event.id),
                )
                if "start" in request.data:
                    start = request.data["start"]
                    start = TypeAdapter(NaiveDatetime).validate_python(
                        start, strict=True
                    )
                    data.start = start
                if "end" in request.data:
                    end = request.data["end"]
                    end = TypeAdapter(NaiveDatetime).validate_python(end, strict=True)
                    data.end = end
                if "timezone" in request.data:
                    timezone = request.data["timezone"]
                    timezone = TypeAdapter(Timezone).validate_python(
                        timezone, strict=True
                    )
                    data.timezone = timezone
                if "recurrence" in request.data:
                    recurrence = request.data["recurrence"]
                    recurrence = TypeAdapter(tm.Recurrence).validate_python(
                        recurrence, strict=True
                    )
                    data.recurrence = recurrence

                emitimes_event = await self._emitimes.upsert_event(data)
            except te.EmitimesError as e:
                raise ee.EmitimesError(str(e)) from e

        event = self._merge_events(database_event, emitimes_event)

        self._emit_event_updated_event(event)

        return em.UpdateResponse(event=event)

    async def delete(
        self,
        request: em.DeleteRequest,
    ) -> em.DeleteResponse:
        """Delete an event."""

        async with self._prisma.tx() as transaction:
            try:
                database_event = await transaction.event.delete(
                    where=request.where,
                    include=request.include,
                )
            except pe.DataError as e:
                raise ee.ValidationError(str(e)) from e
            except pe.PrismaError as e:
                raise ee.DatabaseError(str(e)) from e

            if database_event is None:
                return em.DeleteResponse(event=None)

            try:
                emitimes_event = await self._emitimes.get_event(
                    id=UUID(database_event.id),
                )
                await self._emitimes.delete_event(
                    id=UUID(database_event.id),
                )
            except te.EmitimesError as e:
                raise ee.EmitimesError(str(e)) from e

        event = self._merge_events(database_event, emitimes_event)

        self._emit_event_deleted_event(event)

        return em.DeleteResponse(event=event)
