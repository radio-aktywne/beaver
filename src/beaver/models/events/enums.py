from enum import StrEnum


class EventType(StrEnum):
    """Event types."""

    TEST = "test"
    SHOW_CREATED = "show-created"
    SHOW_UPDATED = "show-updated"
    SHOW_DELETED = "show-deleted"
    EVENT_CREATED = "event-created"
    EVENT_UPDATED = "event-updated"
    EVENT_DELETED = "event-deleted"
