from uuid import UUID

from beaver.services.data.howlite import errors as he, models as hm
from beaver.services.data.howlite.service import HowliteService
from beaver.services.persistence.reader import errors as e, models as m


class RecordReader:
    """Read complete records from both stores."""

    def __init__(self, howlite: HowliteService) -> None:
        self._howlite = howlite

    async def read_event(self, event: m.SapphireEvent) -> m.Event:
        """Read a complete event and its requested relations."""
        try:
            request = hm.GetEventRequest(id=UUID(event.id))
            response = await self._howlite.get_event(request)
        except he.NotFoundError as ex:
            raise e.MissingHowliteEventError(event.id) from ex
        except he.ServiceError as ex:
            raise e.ServiceError from ex

        return m.Event(
            id=event.id,
            type=event.type,
            show_id=event.showId,
            show=await self.read_show(event.show) if event.show is not None else None,
            start=response.event.start,
            duration=response.event.duration,
            timezone=response.event.timezone,
            recurrence=response.event.recurrence,
            include=response.event.include,
            exclude=response.event.exclude,
        )

    async def read_show(self, show: m.SapphireShow) -> m.Show:
        """Read a complete show and its requested relations."""
        return m.Show(
            id=show.id,
            title=show.title,
            description=show.description,
            events=[await self.read_event(event) for event in show.events]
            if show.events is not None
            else None,
        )
