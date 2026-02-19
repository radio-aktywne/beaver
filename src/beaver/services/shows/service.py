import builtins
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from typing import cast
from uuid import UUID

from litestar.channels import ChannelsPlugin

from beaver.models.events import events as eev
from beaver.models.events import shows as sev
from beaver.models.events.types import Event
from beaver.services.howlite import errors as hle
from beaver.services.howlite import models as hlm
from beaver.services.howlite.service import HowliteService
from beaver.services.sapphire import errors as spe
from beaver.services.sapphire import models as spm
from beaver.services.sapphire import types as spt
from beaver.services.sapphire.service import SapphireService
from beaver.services.shows import errors as e
from beaver.services.shows import models as m


class ShowsService:
    """Service to manage shows."""

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
        data = event.model_dump_json(round_trip=True)
        self._channels.publish(data, "events")

    def _emit_show_created_event(self, show: m.Show) -> None:
        self._emit_event(
            sev.ShowCreatedEvent(data=sev.ShowCreatedEventData(show=sev.Show.map(show)))
        )

    def _emit_show_updated_event(self, show: m.Show) -> None:
        self._emit_event(
            sev.ShowUpdatedEvent(data=sev.ShowUpdatedEventData(show=sev.Show.map(show)))
        )

    def _emit_show_deleted_event(self, show: m.Show) -> None:
        self._emit_event(
            sev.ShowDeletedEvent(data=sev.ShowDeletedEventData(show=sev.Show.map(show)))
        )

    def _emit_event_updated_event(self, event: m.Event) -> None:
        self._emit_event(
            eev.EventUpdatedEvent(
                data=eev.EventUpdatedEventData(event=eev.Event.map(event))
            )
        )

    def _emit_event_deleted_event(self, event: m.Event) -> None:
        self._emit_event(
            eev.EventDeletedEvent(
                data=eev.EventDeletedEventData(event=eev.Event.map(event))
            )
        )

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except hle.ServiceError as ex:
            raise e.HowliteError from ex
        except spe.DataError as ex:
            raise e.ValidationError from ex
        except spe.ServiceError as ex:
            raise e.SapphireError from ex

    async def _map_event(self, dsevent: spm.Event) -> m.Event:
        request = hlm.GetEventRequest(id=UUID(dsevent.id))

        with self._handle_errors():
            res = await self._howlite.get_event(request)

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

    async def count(self, request: m.CountRequest) -> m.CountResponse:
        """Count shows."""
        with self._handle_errors():
            count = await self._sapphire.show.count(where=request.where)

        return m.CountResponse(count=count)

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List all shows."""
        with self._handle_errors():
            shows = await self._sapphire.show.find_many(
                take=request.limit,
                skip=request.offset,
                where=request.where,
                include=request.include,
                order=builtins.list(request.order)
                if isinstance(request.order, Sequence)
                else request.order,
            )

        return m.ListResponse(shows=[await self._map_show(show) for show in shows])

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get show."""
        with self._handle_errors():
            show = await self._sapphire.show.find_unique(
                where=request.where, include=request.include
            )

        if show is None:
            return m.GetResponse(show=None)

        return m.GetResponse(show=await self._map_show(show))

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create show."""
        with self._handle_errors():
            show = await self._sapphire.show.create(
                data=cast("spt.ShowCreateInput", request.data), include=request.include
            )

        show = await self._map_show(show)
        self._emit_show_created_event(show)

        return m.CreateResponse(show=show)

    async def _update_handle_events(
        self, transaction: SapphireService, old: spm.Show, new: spm.Show
    ) -> Sequence[spm.Event]:
        events = []

        if new.id != old.id:
            events = await transaction.event.find_many(where={"showId": old.id})

            ids = [event.id for event in events]

            await transaction.event.delete_many(where={"id": {"in": ids}})

            await transaction.event.create_many(
                data=[
                    {
                        "id": event.id,
                        "showId": new.id,
                        "type": event.type,
                    }
                    for event in events
                ]
            )

            events = await transaction.event.find_many(where={"id": {"in": ids}})

        return events

    async def update(self, request: m.UpdateRequest) -> m.UpdateResponse:
        """Update show."""
        async with self._sapphire.tx() as transaction:
            with self._handle_errors():
                old = await transaction.show.find_unique(where=request.where)

                if old is None:
                    return m.UpdateResponse(show=None)

                new = await transaction.show.update(
                    data=cast("spt.ShowUpdateInput", request.data),
                    where=request.where,
                    include=request.include,
                )

                if new is None:
                    return m.UpdateResponse(show=None)

                events = await self._update_handle_events(transaction, old, new)

        new = await self._map_show(new)
        events = [await self._map_event(event) for event in events]

        self._emit_show_updated_event(new)
        for event in events:
            self._emit_event_updated_event(event)

        return m.UpdateResponse(show=new)

    async def _delete_handle_events(
        self, transaction: SapphireService, show: spm.Show
    ) -> Sequence[spm.Event]:
        events = await transaction.event.find_many(where={"showId": show.id})

        await transaction.event.delete_many(
            where={"id": {"in": [event.id for event in events]}}
        )

        for event in events:
            req = hlm.DeleteEventRequest(id=UUID(event.id))

            await self._howlite.delete_event(req)

        return events

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete show."""
        async with self._sapphire.tx() as transaction:
            with self._handle_errors():
                show = await transaction.show.delete(
                    where=request.where, include=request.include
                )

                if show is None:
                    return m.DeleteResponse(show=None)

                events = await self._delete_handle_events(transaction, show)

        show = await self._map_show(show)
        events = [await self._map_event(event) for event in events]

        self._emit_show_deleted_event(show)
        for event in events:
            self._emit_event_deleted_event(event)

        return m.DeleteResponse(show=show)
