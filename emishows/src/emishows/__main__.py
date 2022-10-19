"""Main script.

This module provides basic CLI entrypoint.

"""
import logging
import time
from pathlib import Path
from typing import List, Optional

import typer
import uvicorn
from django.core.management import call_command, CommandError
from typer import FileText

from emishows import log
from emishows.asgi import build_app
from emishows.config import ConfigLoader, Config, EmitimesConfig
from emishows.events import Calendar, calendars

cli = typer.Typer()  # this is actually callable and thus can be an entry point

logger = logging.getLogger(__name__)


def wait_for_certificates(directory: Path) -> None:
    filenames = ["ca.pem", "client.cert.pem", "client.key.pem"]
    files = [directory / filename for filename in filenames]

    while not all(file.exists() for file in files):
        typer.echo("Waiting for certificates...")
        time.sleep(1)

    with open("/etc/ssl/certs/ca-certificates.crt", "a") as f:
        f.write(files[0].read_text())


def wait_for_database() -> None:
    while True:
        typer.echo("Waiting for database...")
        try:
            call_command("wait_for_database")
            break
        except CommandError:
            time.sleep(1)


def create_calendar(config: EmitimesConfig) -> None:
    calendars["emitimes"] = Calendar(
        url=f"http://{config.host}:{config.port}",
        name=config.calendar,
        user=config.user,
        password=config.password,
    )


def setup(config: Config) -> None:
    wait_for_certificates(config.certs_dir)
    wait_for_database()
    call_command("migrate", "--no-input")
    create_calendar(config.emitimes)


@cli.command()
def main(
    config_file: Optional[FileText] = typer.Option(
        None, "--config-file", "-C", dir_okay=False, help="Configuration file."
    ),
    config: Optional[List[str]] = typer.Option(
        None, "--config", "-c", help="Configuration entries."
    ),
    verbosity: log.Verbosity = typer.Option(
        "INFO", "--verbosity", "-v", help="Verbosity level."
    ),
) -> None:
    """Command line interface for emishows."""

    log.configure(verbosity)

    logger.info("Loading config...")
    try:
        config = ConfigLoader.load(config_file, config)
    except ValueError as e:
        logger.error("Failed to parse config!", exc_info=e)
        raise typer.Exit(1)
    logger.info("Config loaded!")

    app = build_app()
    setup(config)
    uvicorn.run(app, host=config.host, port=config.port)


if __name__ == "__main__":
    # entry point for "python -m"
    cli()
