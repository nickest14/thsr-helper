import logging

import typer

from thsr_helper.booking.booking_flow import BookingFlow

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command(name="order")
def order():
    """
    Booking the ticket
    """
    flow = BookingFlow()
    flow.run()
