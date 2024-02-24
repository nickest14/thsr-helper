from collections import namedtuple
from typing import Tuple
import json
import logging

from requests.models import Response
from rich.console import Console
from rich.table import Table
import typer

from .utils import fill_code
from .parser import (
    BookingFlowParser,
    ConfirmTrainParser,
    InitPageParser,
    ConfirmTicketParser,
    Ticket,
)
from .schema import BookingModel, ConfirmTrainModel, Train, ConfirmTicketModel
from .constants import STATION_MAP, TicketType
from thsr_helper.booking.requests import HTTPRequest


logger = logging.getLogger(__name__)

Error = namedtuple("Error", ["msg"])


class BaseFlow:
    def __init__(self, client: HTTPRequest, conditions: dict[str, any]) -> None:
        self.client = client
        self.conditions = conditions
        self.parser = None


class BookingFlow:
    def __init__(self, config: dict[str, any] = None) -> None:
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
        train_response, confirm_model = ConfirmTrainFlow(
            self.client, self.config.get("conditions"), booking_response
        ).run()
        if not confirm_model or self.check_error(train_response):
            return

        # Final page. Ticket confirmation.
        ticket_response, ticket_model = ConfirmTicketFlow(
            self.client,
            self.config.get("conditions"),
            self.config.get("user"),
            train_response,
        ).run()
        if self.check_error(ticket_response):
            return
        page = self.parser.html_to_soup(ticket_response)
        ticket = self.parser.parse_booking_result(page)
        self.show_ticket(ticket)

    def show_ticket(self, ticket: Ticket) -> None:
        console = Console()
        typer.secho(
            "-------------- 訂位結果 --------------", fg=typer.colors.BRIGHT_YELLOW
        )
        typer.secho(f"繳費期限: {ticket.payment_deadline}", fg=typer.colors.BRIGHT_CYAN)
        typer.secho(f"票數: {ticket.ticket_num_info}", fg=typer.colors.BRIGHT_CYAN)
        typer.secho(f"總價: {ticket.price}", fg=typer.colors.BRIGHT_CYAN)
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
            ticket.date,
            ticket.id,
            ticket.start_station,
            ticket.dest_station,
            ticket.depart_time,
            ticket.arrival_time,
            ticket.train_id,
        )
        console.print(table)

    def check_error(self, resp: Response) -> None:
        page = self.parser.html_to_soup(resp)
        if errors := self.parser.parse_response_error(page):
            self.errors.extend(errors)
            self.show_error()
            return True

    def show_error(self):
        for error in self.errors:
            logger.warning(f"[gray37]Error: {error.msg}[/]", extra={"markup": True})


class InitPageFlow(BaseFlow):
    def __init__(self, client: HTTPRequest, conditions: dict[str, any]) -> None:
        super().__init__(client, conditions)
        self.parser = InitPageParser

    def run(self) -> Tuple[bytes, BookingModel]:
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


class ConfirmTrainFlow(BaseFlow):
    def __init__(
        self, client: HTTPRequest, conditions: dict[str, any], booking_response: bytes
    ) -> None:
        super().__init__(client, conditions)
        self.booking_response = booking_response
        self.parser = ConfirmTrainParser

    def run(self) -> Tuple[bytes, ConfirmTrainModel | None]:
        page = self.parser.html_to_soup(self.booking_response)
        self.trains = self.parser.parse_trains(page)
        selected_train = self.choose_train()
        if not selected_train:
            logger.warning(
                "[dodger_blue1]Error: No available train to select.",
                extra={"markup": True},
            )
            return None, None
        confirm_model = ConfirmTrainModel(selected_train=selected_train)
        dict_params = json.loads(confirm_model.json(by_alias=True))
        confirm_response = self.client.submit_train(dict_params).content
        return confirm_response, confirm_model

    def choose_train(self) -> Train:
        for train in self.trains:
            # TODO: Support discount and student ticket
            if train.discount_str != "":
                continue
            start_hour, end_hour = self.conditions.get("time_range")
            hour = int(train.depart.split(":")[0])
            if start_hour <= hour <= end_hour:
                return train.form_value
        return None


class ConfirmTicketFlow(BaseFlow):
    def __init__(
        self,
        client: HTTPRequest,
        conditions: dict[str, any],
        user_info: dict[str, any],
        train_response: bytes,
    ) -> None:
        super().__init__(client, conditions)
        self.user_info = user_info
        self.train_response = train_response
        self.parser = ConfirmTicketParser

    def run(self) -> Tuple[bytes, ConfirmTicketModel | None]:
        page = self.parser.html_to_soup(self.train_response)
        ticket_model = ConfirmTicketModel(
            personal_id=self.user_info.get("personal_id"),
            phone_num=self.user_info.get("phone_number"),
            member_radio=self.parser.parse_member_radio(page),
        )
        if email := self.user_info.get("email"):
            ticket_model.email = email

        # TODO: Support early bird and processenger count

        dict_params = json.loads(ticket_model.json(by_alias=True))
        ticket_response = self.client.submit_ticket(dict_params).content
        return ticket_response, ticket_model
