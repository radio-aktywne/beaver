import uvicorn
from litestar import Litestar

from beaver.config.models import ServerConfig


class Server:
    """Server for the application.

    Args:
        app: The application.
        config: The configuration for the server.
    """

    def __init__(self, app: Litestar, config: ServerConfig) -> None:
        self._app = app
        self._config = config

    def run(self) -> None:
        """Run the server."""

        uvicorn.run(
            self._app,
            host=self._config.host,
            port=self._config.port,
            forwarded_allow_ips=self._config.trusted,
        )
