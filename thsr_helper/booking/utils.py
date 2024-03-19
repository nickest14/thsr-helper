import io

from PIL import Image
from rich.console import Console
from rich.table import Table
import typer

from .schema import Record


def fill_code(img_resp: bytes, manual: bool = True) -> str:
    if manual:
        typer.secho(
            "Please enter the verification code: ", fg=typer.colors.BRIGHT_YELLOW
        )
        with Image.open(io.BytesIO(img_resp)) as image:
            image.show()
            return input()
    else:
        # Implement image recognition here by yourself
        return ""


def show_ticket(record: Record) -> None:
    console = Console()
    typer.secho(f"繳費期限: {record.payment_deadline}", fg=typer.colors.BRIGHT_CYAN)
    typer.secho(f"訂票身分證: {record.personal_id}", fg=typer.colors.BRIGHT_CYAN)
    typer.secho(f"票數: {record.ticket_num_info}", fg=typer.colors.BRIGHT_CYAN)
    typer.secho(f"總價: {record.price}", fg=typer.colors.BRIGHT_CYAN)
    table = Table(show_header=True, header_style="bold dark_magenta")
    cols = [
        {"field": "日期", "style": "light_yellow3"},
        {"field": "訂位代號", "style": "dark_red"},
        {"field": "起程站", "style": ""},
        {"field": "到達站", "style": ""},
        {"field": "出發時間", "style": ""},
        {"field": "到達時間", "style": ""},
        {"field": "車次", "style": ""},
    ]
    for col in cols:
        table.add_column(col.get("field"), style=col.get("style"), justify="right")
    table.add_row(
        record.date,
        record.id,
        record.start_station,
        record.dest_station,
        record.depart_time,
        record.arrival_time,
        record.train_id,
    )
    console.print(table)
