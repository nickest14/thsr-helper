from collections import defaultdict
from datetime import datetime
from typing import Tuple
import logging

import typer
from tomlkit import dumps

from thsr_helper.booking.constants import ThsrTime, Stations, TrainRequirement
from thsr_helper.config.utils import ConfigManager
from thsr_helper.config.validate import (
    validate_personal_id,
    validate_phone_number,
    validate_time_range,
    validate_email,
    validate_ids,
)

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command(name="ls")
def ls():
    """
    Show the config settings
    """
    if config := ConfigManager.get_config():
        typer.secho(f"{dumps(config)}", fg=typer.colors.CYAN)


@app.command(name="update")
def update(
    personal_id: str = typer.Option(
        None, callback=validate_personal_id, help="ID number"
    ),
    phone_number: str = typer.Option(
        None, callback=validate_phone_number, help="Phone number"
    ),
    email: str = typer.Option(None, callback=validate_email, help="Email"),
    start_station: Stations = typer.Option(
        None, case_sensitive=False, help="Choose the start station"
    ),
    dest_station: Stations = typer.Option(
        None, case_sensitive=False, help="Choose the destination station"
    ),
    adult_ticket_num: int = typer.Option(None, help="Adult ticket number"),
    adult_ids: str = typer.Option(
        None,
        callback=validate_ids,
        help="Adult IDs, early bird needed; use a comma to separate.",
    ),
    child_ticket_num: int = typer.Option(None, help="Child ticket number"),
    disabled_ticket_num: int = typer.Option(None, help="Disabled ticket number"),
    disabled_ids: str = typer.Option(
        None,
        callback=validate_ids,
        help="Disabled IDs are always required; use a comma to separate them.",
    ),
    elder_ticket_num: int = typer.Option(None, help="Elder ticket number"),
    elder_ids: str = typer.Option(
        None,
        callback=validate_ids,
        help="Elder IDs are always required; use a comma to separate them.",
    ),
    college_ticket_num: int = typer.Option(None, help="College ticket number"),
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
    train_requirement: TrainRequirement = typer.Option(
        None,
        case_sensitive=False,
        help="Train requirement, 0: all, 1: early bird, 2: normal",
    ),
):
    """
    Update the config file
    """
    options = defaultdict(dict)
    attributes = {
        "user": {
            "personal_id": personal_id,
            "phone_number": phone_number,
            "email": email,
        },
        "conditions": {
            "start_station": start_station,
            "dest_station": dest_station,
            "adult_ticket_num": adult_ticket_num,
            "adult_ids": adult_ids,
            "child_ticket_num": child_ticket_num,
            "disabled_ticket_num": disabled_ticket_num,
            "disabled_ids": disabled_ids,
            "elder_ticket_num": elder_ticket_num,
            "elder_ids": elder_ids,
            "college_ticket_num": college_ticket_num,
            "train_requirement": train_requirement,
            "date": date,
            "time_range": time_range,
            "thsr_time": thsr_time,
        },
    }

    for table_name, table_attributes in attributes.items():
        for attr_name, attr_val in table_attributes.items():
            if isinstance(attr_val, (int, str)) and attr_val:
                options[table_name][attr_name] = attr_val
            elif isinstance(attr_val, tuple) and all(attr_val):
                options[table_name][attr_name] = attr_val

    ConfigManager().update_config(options)
