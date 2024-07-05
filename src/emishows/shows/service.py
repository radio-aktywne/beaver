from typing import TypeVar

from litestar.channels import ChannelsPlugin
from prisma import Prisma
from prisma import errors as pe

from emishows.models import events as ev
from emishows.shows import errors as se
from emishows.shows import models as sm

T = TypeVar("T")


class ShowsService:
    """Service to manage shows."""

    def __init__(self, prisma: Prisma, channels: ChannelsPlugin) -> None:
        self._prisma = prisma
        self._channels = channels

    def _emit_event(self, event: ev.Event) -> None:
        """Emit an event."""

        data = event.model_dump_json(by_alias=True)
        self._channels.publish(data, "events")

    def _normalize_show(self, show: sm.Show) -> sm.Show:
        """Normalize a show."""

        return sm.Show(
            id=show.id,
            title=show.title,
            description=show.description,
        )

    def _emit_show_created_event(self, show: sm.Show) -> None:
        """Emit a show created event."""

        show = self._normalize_show(show)
        event = ev.ShowCreatedEvent(data=ev.ShowCreatedEventData(show=show))
        self._emit_event(event)

    def _emit_show_updated_event(self, show: sm.Show) -> None:
        """Emit a show updated event."""

        show = self._normalize_show(show)
        event = ev.ShowUpdatedEvent(data=ev.ShowUpdatedEventData(show=show))
        self._emit_event(event)

    def _emit_show_deleted_event(self, show: sm.Show) -> None:
        """Emit a show deleted event."""

        show = self._normalize_show(show)
        event = ev.ShowDeletedEvent(data=ev.ShowDeletedEventData(show=show))
        self._emit_event(event)

    async def count(
        self,
        request: sm.CountRequest,
    ) -> sm.CountResponse:
        """Count shows."""

        try:
            count = await self._prisma.show.count(
                where=request.where,
            )
        except pe.DataError as e:
            raise se.ValidationError(str(e)) from e
        except pe.PrismaError as e:
            raise se.DatashowsError(str(e)) from e

        return sm.CountResponse(count=count)

    async def list(
        self,
        request: sm.ListRequest,
    ) -> sm.ListResponse:
        """List all shows."""

        try:
            shows = await self._prisma.show.find_many(
                take=request.limit,
                skip=request.offset,
                where=request.where,
                include=request.include,
                order=request.order,
            )
        except pe.DataError as e:
            raise se.ValidationError(str(e)) from e
        except pe.PrismaError as e:
            raise se.DatashowsError(str(e)) from e

        return sm.ListResponse(shows=shows)

    async def get(
        self,
        request: sm.GetRequest,
    ) -> sm.GetResponse:
        """Get a show."""

        try:
            show = await self._prisma.show.find_unique(
                where=request.where,
                include=request.include,
            )
        except pe.DataError as e:
            raise se.ValidationError(str(e)) from e
        except pe.PrismaError as e:
            raise se.DatashowsError(str(e)) from e

        return sm.GetResponse(show=show)

    async def create(
        self,
        request: sm.CreateRequest,
    ) -> sm.CreateResponse:
        """Create a show."""

        try:
            show = await self._prisma.show.create(
                data=request.data,
                include=request.include,
            )
        except pe.DataError as e:
            raise se.ValidationError(str(e)) from e
        except pe.PrismaError as e:
            raise se.DatashowsError(str(e)) from e

        self._emit_show_created_event(show)

        return sm.CreateResponse(show=show)

    async def update(
        self,
        request: sm.UpdateRequest,
    ) -> sm.UpdateResponse:
        """Update a show."""

        try:
            show = await self._prisma.show.update(
                data=request.data,
                where=request.where,
                include=request.include,
            )
        except pe.DataError as e:
            raise se.ValidationError(str(e)) from e
        except pe.PrismaError as e:
            raise se.DatashowsError(str(e)) from e

        if show is not None:
            self._emit_show_updated_event(show)

        return sm.UpdateResponse(show=show)

    async def delete(
        self,
        request: sm.DeleteRequest,
    ) -> sm.DeleteResponse:
        """Delete a show."""

        try:
            show = await self._prisma.show.delete(
                where=request.where,
                include=request.include,
            )
        except pe.DataError as e:
            raise se.ValidationError(str(e)) from e
        except pe.PrismaError as e:
            raise se.DatashowsError(str(e)) from e

        if show is not None:
            self._emit_show_deleted_event(show)

        return sm.DeleteResponse(show=show)
