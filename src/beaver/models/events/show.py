from typing import Literal

from beaver.models.base import SerializableModel
from beaver.models.events import types as t
from beaver.services.shows import models as sm


class Show(SerializableModel):
    """Show data."""

    id: str
    """Identifier of the show."""

    title: str
    """Title of the show."""

    description: str | None
    """Description of the show."""

    @staticmethod
    def map(show: sm.Show) -> "Show":
        return Show(
            id=show.id,
            title=show.title,
            description=show.description,
        )


class ShowCreatedEventData(SerializableModel):
    """Data of a show created event."""

    show: Show
    """Show that was created."""


class ShowCreatedEvent(SerializableModel):
    """Event that is emitted when show is created."""

    type: t.TypeFieldType[Literal["show-created"]] = "show-created"
    created_at: t.CreatedAtFieldType
    data: t.DataFieldType[ShowCreatedEventData]


class ShowUpdatedEventData(SerializableModel):
    """Data of a show updated event."""

    show: Show
    """Show that was updated."""


class ShowUpdatedEvent(SerializableModel):
    """Event that is emitted when show is updated."""

    type: t.TypeFieldType[Literal["show-updated"]] = "show-updated"
    created_at: t.CreatedAtFieldType
    data: t.DataFieldType[ShowUpdatedEventData]


class ShowDeletedEventData(SerializableModel):
    """Data of a show deleted event."""

    show: Show
    """Show that was deleted."""


class ShowDeletedEvent(SerializableModel):
    """Event that is emitted when show is deleted."""

    type: t.TypeFieldType[Literal["show-deleted"]] = "show-deleted"
    created_at: t.CreatedAtFieldType
    data: t.DataFieldType[ShowDeletedEventData]
