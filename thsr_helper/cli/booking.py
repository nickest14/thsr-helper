import logging

import typer

from thsr_helper.booking.booking_flow import BookingFlow
from thsr_helper.config.utils import ConfigManager

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command(name="order")
def order():
    """
    Booking the ticket
    """
    if config := ConfigManager().get_config():
        flow = BookingFlow(config)
        flow.run()
    else:
        logger.warning(
            "[red] Failed to get the config file. Creating the default one. "
            "Remember to update the configuration. [/]",
            extra={"markup": True},
        )
