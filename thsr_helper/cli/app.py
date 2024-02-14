import typer
from typing import Optional
from thsr_helper import __app_name__, __version__
from .config import app as config_app
from .booking import app as booking_app

app = typer.Typer()
app.add_typer(config_app, name="config", help="Check or update config file")
app.add_typer(booking_app, name="booking", help="Booking or check the ticket")


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
