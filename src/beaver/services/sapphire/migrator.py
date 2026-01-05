import os
import subprocess
from collections.abc import Mapping, Sequence

from beaver.config.models import Config


class SapphireMigrator:
    """Migrator class for sapphire database migrations."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _get_command(self) -> Sequence[str]:
        return ["prisma", "migrate", "deploy"]

    def _get_connection_string(self) -> str:
        return self._config.sapphire.sql.url

    def _get_env(self) -> Mapping[str, str]:
        env = os.environ.copy()

        return env | {
            "PRISMA_DB_URL": self._get_connection_string(),
        }

    def migrate(self) -> None:
        """Apply migrations."""
        try:
            subprocess.run(  # noqa: S603
                self._get_command(),
                env=self._get_env(),
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as ex:
            message = ex.stderr.decode() if ex.stderr else "Unknown error."
            raise RuntimeError(message) from ex
