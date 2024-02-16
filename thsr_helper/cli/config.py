from datetime import datetime
from typing import Tuple
import logging

import typer
import tomli
from tomlkit import dump, dumps, table, document, comment, nl

from thsr_helper.booking.constants import ThsrTime
from .utils import get_config_path
from .validate import validate_personal_id, validate_phone_number, validate_time_range

logger = logging.getLogger(__name__)

app = typer.Typer()


def create_default_config(config_file_path: str):
    doc = document()
    doc.add(comment("This is a TOML document."))
    doc.add(nl())

    user = table()
    user.add("personal_id", "")
    user.add("phone_number", "")
    doc.add("user", user)

    conditions = table()
    conditions.add("adult_ticket_num", 1)
    conditions.add("date", "2024/1/1")
    conditions.add("time_range", [])
    conditions.add("thsr_time", "")
    doc["conditions"] = conditions
    with open(config_file_path, mode="wt", encoding="utf-8") as fp:
        dump(doc, fp)


@app.command(name="ls")
def ls():
    """
    Show the config settings
    """
    config_file_path = get_config_path()
    try:
        with open(config_file_path, mode="rb") as fp:
            config = tomli.load(fp)
            typer.secho(f"{dumps(config)}", fg=typer.colors.CYAN)
    except FileNotFoundError as e:
        create_default_config(config_file_path)
        logger.warning(
            f"[gray37]Failed to open config file: {e}[/]", extra={"markup": True}
        )


@app.command(name="update")
def update(
    personal_id: str = typer.Option(
        None, callback=validate_personal_id, help="ID number"
    ),
    phone_number: str = typer.Option(
        None, callback=validate_phone_number, help="Phone number"
    ),
    adult_ticket_num: int = typer.Option(None, help="Adult ticket number"),
    date: datetime = typer.Option(None, formats=["%Y-%m-%d"], help="Ticket date"),
    time_range: Tuple[int, int] = typer.Option(
        (None, None),
        callback=validate_time_range,
        min=0,
        max=24,
        help="Ticket time range",
    ),
    thsr_time: ThsrTime = typer.Option(
        None, case_sensitive=False, help="Choose the thsr time"
    ),
):
    """
    Update the config file
    """
    config_file_path = get_config_path()

    options = {
        "user": {
            "personal_id": personal_id,
            "phone_number": phone_number,
        },
        "conditions": {
            "adult_ticket_num": adult_ticket_num,
            "date": date.strftime("%Y-%m-%d") if date else None,
            "thsr_time": thsr_time,
            "time_range": time_range if (time_range[0] and time_range[1]) else None,
        },
    }
    try:
        with open(config_file_path, mode="r+b") as fp:
            config = tomli.load(fp)
            for section_name, section_data in options.items():
                for key, value in section_data.items():
                    if value:
                        config[section_name][key] = value

            fp.seek(0)
            fp.write(dumps(config).encode("utf-8"))
            fp.truncate()
    except FileNotFoundError as e:
        logger.warning(
            f"[gray37]Failed to open config file: {e}[/]", extra={"markup": True}
        )
        typer.secho("Create the default config file", fg=typer.colors.BRIGHT_YELLOW)
        create_default_config(config_file_path)
