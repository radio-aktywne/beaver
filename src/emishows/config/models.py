from pydantic import BaseModel, Field

from emishows.config.base import BaseConfig


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = "0.0.0.0"
    """Host to run the server on."""

    port: int = Field(35000, ge=0, le=65535)
    """Port to run the server on."""

    trusted: str | list[str] | None = "*"
    """Trusted IP addresses."""


class DatashowsSQLConfig(BaseModel):
    """Configuration for the SQL API of the datatshows database."""

    host: str = "localhost"
    """Host of the SQL API."""

    port: int = Field(34000, ge=1, le=65535)
    """Port of the SQL API."""

    password: str = "password"
    """Password to authenticate with the SQL API."""

    @property
    def url(self) -> str:
        """URL of the SQL API."""

        return f"postgres://user:{self.password}@{self.host}:{self.port}/database"


class DatashowsConfig(BaseModel):
    """Configuration for the datashows database."""

    sql: DatashowsSQLConfig = DatashowsSQLConfig()
    """Configuration for the SQL API of the datashows database."""


class DatatimesCalDAVConfig(BaseModel):
    """Configuration for the CalDAV API of the datatimes service."""

    scheme: str = "http"
    """Scheme of the CalDAV API."""

    host: str = "localhost"
    """Host of the CalDAV API."""

    port: int | None = Field(36000, ge=1, le=65535)
    """Port of the CalDAV API."""

    path: str | None = None
    """Path of the CalDAV API."""

    user: str = "user"
    """User to authenticate with the CalDAV API."""

    password: str = "password"
    """Password to authenticate with the CalDAV API."""

    calendar: str = "datatimes"
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


class DatatimesConfig(BaseModel):
    """Configuration for the datatimes service."""

    caldav: DatatimesCalDAVConfig = DatatimesCalDAVConfig()
    """Configuration for the CalDAV API of the datatimes service."""


class Config(BaseConfig):
    """Configuration for the service."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""

    datashows: DatashowsConfig = DatashowsConfig()
    """Configuration for the datashows database."""

    datatimes: DatatimesConfig = DatatimesConfig()
    """Configuration for the datatimes service."""

    debug: bool = False
    """Enable debug mode."""
