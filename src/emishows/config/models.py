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


class DatabaseConfig(BaseModel):
    """Configuration for the database."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host to connect to.",
    )
    port: int = Field(
        34000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to connect to.",
    )
    password: str = Field(
        "password",
        title="Password",
        description="Password to authenticate with.",
    )


class EmitimesConfig(BaseModel):
    """Configuration for the Emitimes service."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host to connect to.",
    )
    port: int = Field(
        36000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to connect to.",
    )
    user: str = Field(
        "user",
        title="User",
        description="User to authenticate with.",
    )
    password: str = Field(
        "password",
        title="Password",
        description="Password to authenticate with.",
    )
    calendar: str = Field(
        "emitimes",
        title="Calendar",
        description="Calendar to use.",
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
