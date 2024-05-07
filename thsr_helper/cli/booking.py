import time
from datetime import datetime, timedelta
import logging

import typer

from thsr_helper.booking.booking_flow import BookingFlow
from thsr_helper.booking.models import TinyDBManager
from thsr_helper.config.utils import ConfigManager

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command(name="ls")
def ls(
    start_date: datetime = typer.Option(
        datetime.now() - timedelta(days=6),
        formats=["%Y-%m-%d"],
        help="Start date, default is 7 days ago",
    ),
    end_date: datetime = typer.Option(
        datetime.now(), formats=["%Y-%m-%d"], help="End date"
    ),
):
    """
    Check the booking history
    """
    start_ts = start_date.timestamp()
    end_ts = (
        (end_date + timedelta(days=1)).replace(minute=0, hour=0, second=0).timestamp()
    )
    query_params = {
        "start_ts": int(start_ts),
        "end_ts": int(end_ts),
    }
    db = TinyDBManager()
    db.get_history(query_params)


@app.command(name="order")
def order(
    execution_times: int = typer.Option(
        1, help="How many times to execute ordering ticket."
    ),
):
    """
    Booking the ticket
    """
    if config := ConfigManager().get_config():
        for _ in range(execution_times):
            try:
                flow = BookingFlow(config)
                get_ticket: bool = flow.run()
                if get_ticket:
                    logger.info("Get ticket!")
                    break
            except Exception as e:
                logger.warning(e)
            finally:
                time.sleep(1)
    else:
        logger.warning(
            "[red] Failed to get the config file. Creating the default one. "
            "Remember to update the configuration. [/]",
            extra={"markup": True},
        )
