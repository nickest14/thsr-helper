from collections import namedtuple
from typing import Tuple, Dict, List
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
from .constants import (
    STATION_MAP,
    PassengerType,
    PASSENGER_TYPE_MAP,
    EARLY_BIRD_KEY,
    CHECK_ID_TYPE,
)
from thsr_helper.booking.requests import HTTPRequest
from thsr_helper.config.settings import UserSettings, ConditionSettings

logger = logging.getLogger(__name__)

Error = namedtuple("Error", "msg")


class BaseFlow:
    def __init__(self, client: HTTPRequest, conditions: ConditionSettings) -> None:
        self.client = client
        self.conditions = conditions
        self.parser = None


class BookingFlow:
    def __init__(self, config: dict[str, any] = None) -> None:
        self.client = HTTPRequest()
        self.user_settings = UserSettings(**config.get("user"))
        self.condition_settings = ConditionSettings(**config.get("conditions"))
        self.parser = BookingFlowParser
        self.errors: list[Error] = []

    def run(self) -> None:
        # First page to get booking options.
        booking_response, passenger_info = InitPageFlow(
            self.client, self.condition_settings
        ).run()
        if self.check_error(booking_response):
            return

        # Second page. Train confirmation.
        train_response, selected_train = ConfirmTrainFlow(
            self.client, self.condition_settings, booking_response
        ).run()
        if not selected_train or self.check_error(train_response):
            return

        # Final page. Ticket confirmation.
        ticket_response, error = ConfirmTicketFlow(
            self.client,
            self.condition_settings,
            self.user_settings,
            train_response,
            passenger_info,
            selected_train,
        ).run()
        if error or self.check_error(ticket_response):
            return
        page = self.parser.html_to_soup(ticket_response)
        ticket = self.parser.parse_booking_result(page)
        self.show_ticket(ticket)

    def show_ticket(self, ticket: Ticket) -> None:
        personal_id = self.user_settings.personal_id
        console = Console()
        typer.secho(
            "-------------- 訂位結果 --------------", fg=typer.colors.BRIGHT_YELLOW
        )
        typer.secho(f"繳費期限: {ticket.payment_deadline}", fg=typer.colors.BRIGHT_CYAN)
        typer.secho(f"訂票身分證: {personal_id}", fg=typer.colors.BRIGHT_CYAN)
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
    def __init__(self, client: HTTPRequest, conditions: ConditionSettings) -> None:
        super().__init__(client, conditions)
        self.parser = InitPageParser

    def run(self) -> Tuple[bytes, Dict[PassengerType, int]]:
        init_response: bytes = self.client.booking_page().content
        page = self.parser.html_to_soup(init_response)
        image_url = self.parser.parse_captcha_img_url(page)
        img: bytes = self.client.get_captcha_img(image_url).content

        passenger_info = {
            PassengerType.ADULT: self.conditions.adult_ticket_num or 0,
            PassengerType.CHILD: self.conditions.child_ticket_num or 0,
            PassengerType.DISABLED: self.conditions.disabled_ticket_num or 0,
            PassengerType.ELDER: self.conditions.elder_ticket_num or 0,
            PassengerType.COLLEGE: self.conditions.college_ticket_num or 0,
        }

        booking_model = BookingModel(
            start_station=STATION_MAP.get(self.conditions.start_station),
            dest_station=STATION_MAP.get(self.conditions.dest_station),
            outbound_time=self.conditions.thsr_time,
            outbound_date=self.conditions.date,
            adult_ticket_num=self.convert_ticket_num(
                passenger_info.get(PassengerType.ADULT), PassengerType.ADULT
            ),
            child_ticket_num=self.convert_ticket_num(
                passenger_info.get(PassengerType.CHILD), PassengerType.CHILD
            ),
            disabled_ticket_num=self.convert_ticket_num(
                passenger_info.get(PassengerType.DISABLED), PassengerType.DISABLED
            ),
            elder_ticket_num=self.convert_ticket_num(
                passenger_info.get(PassengerType.ELDER), PassengerType.ELDER
            ),
            college_ticket_num=self.convert_ticket_num(
                passenger_info.get(PassengerType.COLLEGE), PassengerType.COLLEGE
            ),
            seat_prefer=self.parser.parse_seat_prefer_value(page),
            types_of_trip=self.parser.parse_types_of_trip_value(page),
            search_by=self.parser.parse_search_by(page),
            train_requirement=int(self.conditions.train_requirement) or 0,
            security_code=fill_code(img, manual=True),
        )
        dict_params = json.loads(booking_model.json(by_alias=True))
        booking_response = self.client.submit_booking_form(dict_params).content
        return booking_response, passenger_info

    def convert_ticket_num(self, ticket_num: int, passenger_type: PassengerType) -> str:
        return f"{ticket_num}{PASSENGER_TYPE_MAP.get(passenger_type)}"


class ConfirmTrainFlow(BaseFlow):
    def __init__(
        self,
        client: HTTPRequest,
        conditions: ConditionSettings,
        booking_response: bytes,
    ) -> None:
        super().__init__(client, conditions)
        self.booking_response = booking_response
        self.parser = ConfirmTrainParser

    def run(self) -> Tuple[bytes, ConfirmTrainModel | None]:
        page = self.parser.html_to_soup(self.booking_response)
        self.trains = self.parser.parse_trains(page)
        selected_train: Train = self.choose_train()
        if not selected_train:
            logger.warning(
                "[dodger_blue1]Error: No available train to select.",
                extra={"markup": True},
            )
            return None, None
        confirm_model = ConfirmTrainModel(selected_train=selected_train.form_value)
        dict_params = json.loads(confirm_model.json(by_alias=True))
        confirm_response = self.client.submit_train(dict_params).content
        return confirm_response, selected_train

    def choose_train(self) -> Train:
        for train in self.trains:
            start_hour, end_hour = self.conditions.time_range
            hour = int(train.depart.split(":")[0])
            if start_hour <= hour <= end_hour:
                return train
        return None


class ConfirmTicketFlow(BaseFlow):
    def __init__(
        self,
        client: HTTPRequest,
        conditions: ConditionSettings,
        user_settings: UserSettings,
        train_response: bytes,
        passenger_info: Dict[PassengerType, int],
        train: Train,
    ) -> None:
        super().__init__(client, conditions)
        self.user_settings = user_settings
        self.train_response = train_response
        self.passenger_info = passenger_info
        self.train = train
        self.parser = ConfirmTicketParser

    def run(self) -> Tuple[bytes, Error | None]:
        page = self.parser.html_to_soup(self.train_response)
        ticket_model = ConfirmTicketModel(
            personal_id=self.user_settings.personal_id,
            phone_num=self.user_settings.phone_number,
            member_radio=self.parser.parse_member_radio(page),
        )
        if email := self.user_settings.email:
            ticket_model.email = email

        self.params = json.loads(ticket_model.json(by_alias=True))
        if error := self.updated_passenger_id():
            return None, error
        ticket_response = self.client.submit_ticket(self.params).content
        return ticket_response, None

    def updated_passenger_id(self) -> None:
        early_bird = EARLY_BIRD_KEY in self.train.discount_str
        id_check_required = any(
            self.passenger_info.get(pass_type, 0) > 0 for pass_type in CHECK_ID_TYPE
        )

        if early_bird or id_check_required:
            passenger_num = 0
            self.params[
                f"TicketPassengerInfoInputPanel:passengerDataView:{passenger_num}:passengerDataView2:passengerDataInputChoice"
            ] = "0"
            for pass_type, passenger_count in self.passenger_info.items():
                if passenger_count == 0:
                    continue
                pass_ids: List = getattr(
                    self.conditions, f"{pass_type.value}_ids", ""
                ).split(",")
                use_pass_ids, error = self.validate_passenger_id(
                    early_bird, pass_ids, pass_type, passenger_count
                )
                if error:
                    return error

                for idx in range(passenger_count):
                    pass_id = pass_ids[idx] if use_pass_ids else ""
                    self.params[
                        f"TicketPassengerInfoInputPanel:passengerDataView:{passenger_num}:passengerDataView2:passengerDataIdNumber"
                    ] = pass_id

                passenger_num += 1

    def validate_passenger_id(
        self,
        early_bird: bool,
        pass_ids: List[str],
        pass_type: PassengerType,
        passenger_count: int,
    ) -> Tuple[bool, Error]:
        if (
            early_bird and pass_type == PassengerType.ADULT
        ) or pass_type in CHECK_ID_TYPE:
            if len(pass_ids) != passenger_count or not all(pass_ids):
                logger.warning(
                    f"[dark_slate_gray2]Error: {pass_type.value} ids not matched, please updated key: {pass_type.value}_ids in config[/]",
                    extra={"markup": True},
                )
                return None, Error(f"Error: {pass_type.value} ids not matched")
            return True, None
        else:
            return False, None
