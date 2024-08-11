import typer

from emishows.api.app import AppBuilder
from emishows.cli import CliBuilder
from emishows.config.builder import ConfigBuilder
from emishows.config.errors import ConfigError
from emishows.console import FallbackConsoleBuilder
from emishows.server import Server
from emishows.services.datashows.migrator import DatashowsMigrator

cli = CliBuilder().build()


@cli.command()
def main() -> None:
    """Main entry point."""

    console = FallbackConsoleBuilder().build()

    try:
        config = ConfigBuilder().build()
    except ConfigError as ex:
        console.print("Failed to build config!")
        console.print_exception()
        raise typer.Exit(1) from ex

    try:
        app = AppBuilder(config).build()
    except Exception as ex:
        console.print("Failed to build app!")
        console.print_exception()
        raise typer.Exit(2) from ex

    try:
        DatashowsMigrator(config).migrate()
    except Exception as ex:
        console.print("Failed to apply datashows migrations!")
        console.print_exception()
        raise typer.Exit(3) from ex

    try:
        server = Server(app, config.server)
        server.run()
    except Exception as ex:
        console.print("Failed to run server!")
        console.print_exception()
        raise typer.Exit(4) from ex


if __name__ == "__main__":
    cli()
