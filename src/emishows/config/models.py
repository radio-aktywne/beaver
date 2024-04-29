from pydantic import BaseModel, Field

from emishows.config.base import BaseConfig


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = Field(
        "0.0.0.0",
        title="Host",
        description="Host to run the server on.",
    )
    port: int = Field(
        35000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to run the server on.",
    )


class DatabaseSQLConfig(BaseModel):
    """Configuration for the SQL API of the database."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the SQL API.",
    )
    port: int = Field(
        34000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the SQL API .",
    )
    password: str = Field(
        "password",
        title="Password",
        description="Password to authenticate with the SQL API.",
    )

    @property
    def url(self) -> str:
        return f"postgres://user:{self.password}@{self.host}:{self.port}/database"


class DatabaseConfig(BaseModel):
    """Configuration for the database."""

    sql: DatabaseSQLConfig = Field(
        DatabaseSQLConfig(),
        title="SQL",
        description="Configuration for the SQL API of the database.",
    )


class EmitimesCalDAVConfig(BaseModel):
    """Configuration for the CalDAV API of the Emitimes service."""

    scheme: str = Field(
        "http",
        title="Scheme",
        description="Scheme of the CalDAV API.",
    )
    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the CalDAV API.",
    )
    port: int | None = Field(
        36000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the CalDAV API.",
    )
    path: str | None = Field(
        None,
        title="Path",
        description="Path of the CalDAV API.",
    )
    user: str = Field(
        "user",
        title="User",
        description="User to authenticate with the CalDAV API.",
    )
    password: str = Field(
        "password",
        title="Password",
        description="Password to authenticate with the CalDAV API.",
    )
    calendar: str = Field(
        "emitimes",
        title="Calendar",
        description="Calendar to use with the CalDAV API.",
    )

    @property
    def url(self) -> str:
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return f"{url}/{self.user}/{self.calendar}"


class EmitimesConfig(BaseModel):
    """Configuration for the Emitimes service."""

    caldav: EmitimesCalDAVConfig = Field(
        EmitimesCalDAVConfig(),
        title="CalDAV",
        description="Configuration for the CalDAV API of the Emitimes service.",
    )


class Config(BaseConfig):
    """Configuration for the application."""

    server: ServerConfig = Field(
        ServerConfig(),
        title="Server",
        description="Configuration for the server.",
    )
    database: DatabaseConfig = Field(
        DatabaseConfig(),
        title="Database",
        description="Configuration for the database.",
    )
    emitimes: EmitimesConfig = Field(
        EmitimesConfig(),
        title="Emitimes",
        description="Configuration for the Emitimes service.",
    )
