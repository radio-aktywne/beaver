from datetime import datetime, timezone
from typing import Annotated

from pydantic import AfterValidator, AwareDatetime, NaiveDatetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def awareutcnow() -> AwareDatetime:
    """Return the current datetime in UTC with timezone information."""

    return datetime.now(timezone.utc)


def naiveutcnow() -> NaiveDatetime:
    """Return the current datetime in UTC without timezone information."""

    return awareutcnow().replace(tzinfo=None)


def stringify(dt: datetime) -> str:
    """Convert a datetime to a string in ISO 8601 format."""

    return dt.isoformat().replace("+00:00", "Z")


class TimezoneValidationError(ValueError):
    """Timezone validation error."""

    def __init__(self, value: str) -> None:
        super().__init__(f"Invalid time zone: {value}")


def validate_timezone(value: str) -> str:
    """Validate a time zone."""

    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as e:
        raise TimezoneValidationError(value) from e

    return value


Timezone = Annotated[str, AfterValidator(validate_timezone)]
