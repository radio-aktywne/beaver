from pydantic import BaseModel, Field

from beaver.config.base import BaseConfig


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = "0.0.0.0"
    """Host to run the server on."""

    port: int = Field(10500, ge=0, le=65535)
    """Port to run the server on."""

    trusted: str | list[str] | None = "*"
    """Trusted IP addresses."""


class HowliteCalDAVConfig(BaseModel):
    """Configuration for the CalDAV API of the howlite database."""

    scheme: str = "http"
    """Scheme of the CalDAV API."""

    host: str = "localhost"
    """Host of the CalDAV API."""

    port: int | None = Field(10520, ge=1, le=65535)
    """Port of the CalDAV API."""

    path: str | None = None
    """Path of the CalDAV API."""

    user: str = "user"
    """User to authenticate with the CalDAV API."""

    password: str = "password"
    """Password to authenticate with the CalDAV API."""

    calendar: str = "calendar"
    """Calendar to use with the CalDAV API."""

    @property
    def url(self) -> str:
        """URL of the CalDAV API."""

        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return f"{url}/{self.user}/{self.calendar}"


class HowliteConfig(BaseModel):
    """Configuration for the howlite database."""

    caldav: HowliteCalDAVConfig = HowliteCalDAVConfig()
    """Configuration for the CalDAV API of the howlite database."""


class SapphireSQLConfig(BaseModel):
    """Configuration for the SQL API of the datatshows database."""

    host: str = "localhost"
    """Host of the SQL API."""

    port: int = Field(10510, ge=1, le=65535)
    """Port of the SQL API."""

    password: str = "password"
    """Password to authenticate with the SQL API."""

    @property
    def url(self) -> str:
        """URL of the SQL API."""

        return f"postgres://user:{self.password}@{self.host}:{self.port}/database"


class SapphireConfig(BaseModel):
    """Configuration for the sapphire database."""

    sql: SapphireSQLConfig = SapphireSQLConfig()
    """Configuration for the SQL API of the sapphire database."""


class Config(BaseConfig):
    """Configuration for the service."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""

    howlite: HowliteConfig = HowliteConfig()
    """Configuration for the howlite database."""

    sapphire: SapphireConfig = SapphireConfig()
    """Configuration for the sapphire database."""

    debug: bool = False
    """Enable debug mode."""
