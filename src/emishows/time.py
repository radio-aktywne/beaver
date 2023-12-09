from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def utczone() -> ZoneInfo:
    """Return the UTC time zone."""

    return ZoneInfo("Etc/UTC")


def utcnow() -> datetime:
    """Return the current datetime in UTC."""

    return datetime.now(utczone())


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
