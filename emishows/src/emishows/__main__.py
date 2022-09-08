"""Main script.

This module provides basic CLI entrypoint.

"""
import time

import typer
import uvicorn
from django.core.management import call_command

from emishows.asgi import app
from emishows.config import config
from emishows.events import Calendar, calendars

cli = typer.Typer()


def wait_for_certificates() -> None:
    filenames = ["ca.pem", "client.cert.pem", "client.key.pem"]
    files = [config.certs_dir / filename for filename in filenames]

    while not all(file.exists() for file in files):
        typer.echo("Waiting for certificates...")
        time.sleep(1)

    with open("/etc/ssl/certs/ca-certificates.crt", "a") as f:
        f.write(files[0].read_text())


def create_calendar() -> None:
    calendars["emitimes"] = Calendar(
        url=f"http://{config.emitimes_host}:{config.emitimes_port}",
        name=config.emitimes_calendar,
        user=config.emitimes_user,
        password=config.emitimes_password,
    )


def setup() -> None:
    wait_for_certificates()
    call_command("migrate", "--no-input")
    create_calendar()


@cli.command()
def main(
    host: str = typer.Option(
        default="0.0.0.0", help="Host to run the server on"
    ),
    port: int = typer.Option(default=35000, help="Port to run the server on"),
):
    """Command line interface for emishows."""

    setup()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
