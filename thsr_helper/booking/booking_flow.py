from collections import namedtuple
from typing import Tuple
import json
import logging

from requests.models import Response
from .utils import fill_code
from .parser import BookingFlowParser, InitPageParser
from .schema import BookingModel
from .constants import STATION_MAP, TicketType
from thsr_helper.booking.requests import HTTPRequest


logger = logging.getLogger(__name__)

Error = namedtuple("Error", ["msg"])


class BookingFlow:
    def __init__(self, config: dict[str, any]) -> None:
        self.client = HTTPRequest()
        self.config = config
        self.parser = BookingFlowParser
        self.errors: list[Error] = []

    def run(self) -> None:
        # First page to get booking options.
        booking_response, booking_model = InitPageFlow(
            self.client, self.config.get("conditions")
        ).run()
        if self.check_error(booking_response):
            return

        # Second page. Train confirmation.
        train_response = ConfirmTrainFlow(
            self.client, self.config.get("conditions"), booking_model
        ).run()
        if self.check_error(train_response):
            return

    def check_error(self, resp: Response) -> None:
        page = self.parser.html_to_soup(resp)
        if errors := self.parser.parse_response_error(page):
            self.errors.extend(errors)
            self.show_error()
            return True

    def show_error(self):
        for error in self.errors:
            logger.warning(f"[gray37]Error: {error.msg}[/]", extra={"markup": True})


class InitPageFlow:
    def __init__(self, client: HTTPRequest, conditions: dict[str, any]) -> None:
        self.client = client
        self.conditions = conditions
        self.parser = InitPageParser

    def run(self) -> Tuple[Response, int]:
        init_response: bytes = self.client.booking_page().content
        page = self.parser.html_to_soup(init_response)
        image_url = self.parser.parse_captcha_img_url(page)
        img: bytes = self.client.get_captcha_img(image_url).content

        booking_model = BookingModel(
            start_station=STATION_MAP.get(self.conditions["start_station"]),
            dest_station=STATION_MAP.get(self.conditions["dest_station"]),
            outbound_time=self.conditions["thsr_time"],
            outbound_date=self.conditions["date"],
            adult_ticket_num=self.convert_ticket_num(
                TicketType.ADULT, self.conditions["adult_ticket_num"]
            ),
            seat_prefer=self.parser.parse_seat_prefer_value(page),
            types_of_trip=self.parser.parse_types_of_trip_value(page),
            search_by=self.parser.parse_search_by(page),
            security_code=fill_code(img, manual=True),
        )
        dict_params = json.loads(booking_model.json(by_alias=True))
        booking_response = self.client.submit_booking_form(dict_params).content
        return booking_response, booking_model

    def convert_ticket_num(self, ticket_type: TicketType, ticket_num: int) -> str:
        return f"{ticket_num}{ticket_type.value}"


class ConfirmTrainFlow:
    def __init__(
        self, client: HTTPRequest, conditions: dict[str, any], booking_response: bytes
    ) -> None:
        self.client = client
        self.conditions = conditions
        self.booking_response = booking_response

    def run():
        pass
