from collections.abc import Generator, Sequence
from contextlib import contextmanager, suppress
from dataclasses import replace
from uuid import UUID

from beaver.services.consistency.coordination import models as cm
from beaver.services.data.howlite import errors as he, models as hm
from beaver.services.data.sapphire import errors as se, models as sm, types as st
from beaver.services.persistence.reader import errors as re
from beaver.services.persistence.reader.service import RecordReader
from beaver.services.persistence.shows import errors as e, models as m


class ShowsPersistenceService:
    """Service to persist shows and their event relationships."""

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

    async def _rename_show(self, show_id: str, new_id: str) -> sm.Show | None:
        sevents = await self._transaction.sapphire.event.find_many(
            where={"showId": show_id}
        )

        if sevents:
            await self._transaction.sapphire.show.update(
                data={"events": {"set": []}}, where={"id": show_id}
            )

        sshow = await self._transaction.sapphire.show.update(
            data={"id": new_id}, where={"id": show_id}
        )

        if sshow is not None and sevents:
            await self._transaction.sapphire.show.update(
                data={"events": {"connect": [{"id": sevent.id} for sevent in sevents]}},
                where={"id": sshow.id},
            )

        return sshow

    async def _update_event_metadata(self, sshow: sm.Show) -> None:
        sevents = await self._transaction.sapphire.event.find_many(
            where={"showId": sshow.id}
        )

        for sevent in sevents:
            with suppress(he.ServiceError):
                response = await self._transaction.howlite.get_event(
                    hm.GetEventRequest(id=UUID(sevent.id))
                )

                hevent = replace(
                    response.event,
                    summary=sshow.title,
                    description=sshow.description,
                    categories={str(sevent.type)},
                )

                if hevent != response.event:
                    await self._transaction.howlite.upsert_event(
                        hm.UpsertEventRequest(event=hevent)
                    )

    async def _delete_events(self, show_id: str) -> None:
        sevents = await self._transaction.sapphire.event.find_many(
            where={"showId": show_id}
        )

        for sevent in sevents:
            with suppress(he.NotFoundError):
                await self._transaction.howlite.delete_event(
                    hm.DeleteEventRequest(id=UUID(sevent.id))
                )

        await self._transaction.sapphire.event.delete_many(where={"showId": show_id})

    async def count(
        self,
        where: m.ShowWhereInput | None = None,
    ) -> int:
        """Count shows matching the filters."""
        with self._handle_errors():
            return await self._transaction.sapphire.show.count(where=where)

    async def get(
        self,
        where: m.ShowWhereUniqueInput,
        *,
        include: m.ShowInclude | None = None,
    ) -> m.Show | None:
        """Read a show with its requested relations."""
        with self._handle_errors():
            sshow = await self._transaction.sapphire.show.find_unique(
                where=where, include=include
            )

            return await self._reader.read_show(sshow) if sshow is not None else None

    async def list(
        self,
        *,
        where: m.ShowWhereInput | None = None,
        include: m.ShowInclude | None = None,
        take: int | None = None,
        skip: int | None = None,
        order: m.ShowOrderByInput | Sequence[m.ShowOrderByInput] | None = None,
    ) -> Sequence[m.Show]:
        """Read a page of shows and their requested relations."""
        with self._handle_errors():
            if take == 0:
                return []

            sshows = await self._transaction.sapphire.show.find_many(
                where=where,
                include=include,
                take=take,
                skip=skip,
                order=list(order) if isinstance(order, Sequence) else order,
            )

            return [await self._reader.read_show(sshow) for sshow in sshows]

    async def create(
        self,
        data: m.ShowCreateInput,
        *,
        include: m.ShowInclude | None = None,
    ) -> m.Show:
        """Create a show."""
        with self._handle_errors():
            sdata = st.ShowCreateInput(**data)

            sshow = await self._transaction.sapphire.show.create(
                data=sdata, include=include
            )

            return await self._reader.read_show(sshow)

    async def update(
        self,
        data: m.ShowUpdateInput,
        *,
        where: m.ShowWhereUniqueInput,
        include: m.ShowInclude | None = None,
    ) -> m.Show | None:
        """Update a show and its dependent event data."""
        with self._handle_errors():
            if not data:
                return await self.get(where, include=include)

            sshow = await self._transaction.sapphire.show.find_unique(where=where)

            if sshow is None:
                return None

            if "id" in data and data["id"] != sshow.id:
                sshow = await self._rename_show(sshow.id, data["id"])

                if sshow is None:
                    return None

            sdata = st.ShowUpdateInput(**data)

            sshow = await self._transaction.sapphire.show.update(
                data=sdata,
                where={"id": sshow.id},
                include=include,
            )

            if sshow is None:
                return None

            if "title" in data or "description" in data:
                await self._update_event_metadata(sshow)

            return await self._reader.read_show(sshow)

    async def delete(
        self,
        where: m.ShowWhereUniqueInput,
        *,
        include: m.ShowInclude | None = None,
    ) -> m.Show | None:
        """Delete a show and its events, returning the show's previous data."""
        with self._handle_errors():
            sshow = await self._transaction.sapphire.show.find_unique(
                where=where, include=include
            )

            if sshow is None:
                return None

            show = await self._reader.read_show(sshow)

            await self._delete_events(sshow.id)
            await self._transaction.sapphire.show.delete(where={"id": sshow.id})

            return show
