import sys
import importlib

import typer
from typing import Optional
from thsr_helper import __app_name__, __version__

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def handle_callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    return


def register_commands(app: typer.Typer):
    modules: dict[str, str] = {
        "config": "Check or update config file",
        "booking": "Booking or check the ticket",
    }
    for file_name, description in modules.items():
        module = importlib.import_module(f"thsr_helper.cli.{file_name}")
        app.add_typer(module.app, name=file_name, help=description)


def main():
    """
    Main entry point for the CLI application.
    """
    register_commands(app)
    app(prog_name="thsr_helper")
    sys.exit()
