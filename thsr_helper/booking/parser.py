import abc
from typing import Mapping, Any, List

from bs4 import BeautifulSoup
from bs4.element import Tag

from .constants import HTTPConfig
from .schema import Train, Ticket, Error


class BaseParser(metaclass=abc.ABCMeta):
    @classmethod
    def html_to_soup(cls, content: bytes) -> BeautifulSoup:
        return BeautifulSoup(content, features="html.parser")


class BookingFlowParser(BaseParser):
    booking_result: Mapping[str, Any] = {
        "ticket_id": {"name": "p", "attrs": {"class": "pnr-code"}},
        "payment_deadline": {"name": "p", "attrs": {"class": "payment-status"}},
        "phone": {"text": "行動電話"},
        "info": {"name": "table", "attrs": {"class": "table_simple"}},
        "outbound_info": {"text": "去程"},
        "ticket_num": {"name": "p", "text": "票數"},
        "total_price": {"id": "setTrainTotalPriceValue"},
        "train_id": {"id": "setTrainCode0"},
        "depart_time": {"id": "setTrainDeparture0"},
        "arrival_time": {"id": "setTrainArrival0"},
        "depart_station": {"name": "p", "attrs": {"class": "departure-stn"}},
        "arrival_station": {"name": "p", "attrs": {"class": "arrival-stn"}},
        "date": {"name": "span", "attrs": {"class": "date"}},
    }

    error_feedback: Mapping[str, Any] = {
        "name": "span",
        "attrs": {"class": "feedbackPanelERROR"},
    }

    @classmethod
    def parse_booking_result(cls, page: BeautifulSoup) -> Ticket:
        booking_id = page.find(**cls.booking_result["ticket_id"]).find("span").text
        deadline = (
            page.find(**cls.booking_result["payment_deadline"])
            .find_next(text="（付款期限：")
            .find_next()
            .text
        )
        total_price = page.find(**cls.booking_result["total_price"]).text
        train_id = page.find(**cls.booking_result["train_id"]).text
        depart_time = page.find(**cls.booking_result["depart_time"]).text
        arrival_time = page.find(**cls.booking_result["arrival_time"]).text
        depart_station = (
            page.find(**cls.booking_result["depart_station"]).find_next().text
        )
        arrival_station = (
            page.find(**cls.booking_result["arrival_station"]).find_next().text
        )
        ticket_num_info = page.find(**cls.booking_result["ticket_num"]).find_next().text
        ticket_num_info = ticket_num_info.strip().replace("\xa0", " ")
        date = page.find(**cls.booking_result["date"]).find_next().text

        ticket = Ticket(
            id=booking_id,
            payment_deadline=deadline,
            ticket_num_info=ticket_num_info,
            price=total_price,
            train_id=train_id,
            depart_time=depart_time,
            arrival_time=arrival_time,
            start_station=depart_station,
            dest_station=arrival_station,
            date=date,
        )
        return ticket

    @classmethod
    def parse_response_error(cls, page: BeautifulSoup) -> List[Error]:
        items = page.find_all(**cls.error_feedback)
        return [Error(item.text) for item in items]


class InitPageParser(BaseParser):
    booking_page: Mapping[str, Any] = {
        "security_code_img": {"id": "BookingS1Form_homeCaptcha_passCode"},
        "seat_prefer_radio": {"id": "BookingS1Form_seatCon_seatRadioGroup"},
        "types_of_trip": {"id": "BookingS1Form_tripCon_typesoftrip"},
    }

    @classmethod
    def parse_captcha_img_url(cls, page: BeautifulSoup) -> str:
        return HTTPConfig.BASE_URL + page.find(
            **cls.booking_page["security_code_img"]
        ).get("src")

    @classmethod
    def parse_seat_prefer_value(cls, page: BeautifulSoup) -> str:
        options = page.find(**cls.booking_page["seat_prefer_radio"])
        preferred_seat = options.find_next(selected="selected")
        return preferred_seat.attrs["value"]

    @classmethod
    def parse_types_of_trip_value(cls, page: BeautifulSoup) -> int:
        options = page.find(**cls.booking_page["types_of_trip"])
        tag = options.find_next(selected="selected")
        return int(tag.attrs["value"])

    @classmethod
    def parse_search_by(cls, page: BeautifulSoup) -> str:
        candidates = page.find_all("input", {"name": "bookingMethod"})
        tag = next((cand for cand in candidates if "checked" in cand.attrs))
        return tag.attrs["value"]


class ConfirmTrainParser(BaseParser):
    train_attr: Mapping[str, Any] = {
        "from_html": {"attrs": {"class": "result-item"}},
        "train_id": {"id": "QueryCode"},
        "depart": {"id": "QueryDeparture"},
        "arrival": {"id": "QueryArrival"},
        "duration": {"attrs": {"class": "duration"}},
        "early_bird_discount": {"name": "p", "attrs": {"class": "early-bird"}},
        "college_student_discount": {"name": "p", "attrs": {"class": "student"}},
        "form_value": {
            "name": "input",
            "attrs": {"name": "TrainQueryDataViewPanel:TrainGroup"},
        },
    }

    @classmethod
    def _parse_discount(cls, item: Tag) -> str:
        discounts = []
        if tag := item.find(**cls.train_attr.get("early_bird_discount")):
            discounts.append(tag.find_next().text)
        if tag := item.find(**cls.train_attr.get("college_student_discount")):
            discounts.append(tag.find_next().text)
        return ", ".join(discounts)

    @classmethod
    def parse_trains(cls, page: BeautifulSoup) -> List[Train]:
        trains: List[Train] = []
        avail: List[Tag] = page.find_all("label", **cls.train_attr.get("from_html"))
        for item in avail:
            train_id = int(item.find(**cls.train_attr.get("train_id")).text)
            depart_time = item.find(**cls.train_attr.get("depart")).text
            arrival_time = item.find(**cls.train_attr.get("arrival")).text
            travel_time = (
                item.find(**cls.train_attr.get("duration"))
                .find_next("span", {"class": "material-icons"})
                .fetchNextSiblings()[0]
                .text
            )
            discount_str = cls._parse_discount(item)
            form_value = item.find(**cls.train_attr.get("form_value")).attrs["value"]
            trains.append(
                Train(
                    id=train_id,
                    depart=depart_time,
                    arrive=arrival_time,
                    travel_time=travel_time,
                    discount_str=discount_str,
                    form_value=form_value,
                )
            )
        return trains


class ConfirmTicketParser(BaseParser):
    ticket_attr: Mapping[str, Any] = {
        "name": "input",
        "attrs": {
            "name": "TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup"
        },
    }

    @classmethod
    def parse_member_radio(cls, page: BeautifulSoup):
        candidates = page.find_all(**cls.ticket_attr)
        tag = next((cand for cand in candidates if "checked" in cand.attrs))
        return tag.attrs["value"]
