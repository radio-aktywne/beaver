import typer

from beaver.api.app import AppBuilder
from beaver.cli import CliBuilder
from beaver.config.builder import ConfigBuilder
from beaver.config.errors import ConfigError
from beaver.console import FallbackConsoleBuilder
from beaver.server import Server
from beaver.services.sapphire.migrator import SapphireMigrator

cli = CliBuilder().build()


@cli.command()
def main() -> None:
    """Run main entry point."""
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
        SapphireMigrator(config).migrate()
    except Exception as ex:
        console.print("Failed to apply sapphire migrations!")
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
