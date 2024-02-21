import abc
from collections import namedtuple
from typing import Mapping, Any

from bs4 import BeautifulSoup

from .constants import HTTPConfig

Error = namedtuple("Error", ["msg"])

BOOKING_PAGE: Mapping[str, Any] = {
    "security_code_img": {"id": "BookingS1Form_homeCaptcha_passCode"},
    "seat_prefer_radio": {"id": "BookingS1Form_seatCon_seatRadioGroup"},
    "types_of_trip": {"id": "BookingS1Form_tripCon_typesoftrip"},
}

ERROR_FEEDBACK: Mapping[str, Any] = {
    "name": "span",
    "attrs": {"class": "feedbackPanelERROR"},
}


class BaseParser(metaclass=abc.ABCMeta):
    @classmethod
    def html_to_soup(cls, content: bytes) -> BeautifulSoup:
        return BeautifulSoup(content, features="html.parser")


class BookingFlowParser(BaseParser):
    @classmethod
    def parse_response_error(cls, page: BeautifulSoup):
        items = page.find_all(**ERROR_FEEDBACK)
        return [Error(item.text) for item in items]


class InitPageParser(BaseParser):
    @classmethod
    def parse_captcha_img_url(cls, page: BeautifulSoup) -> str:
        return HTTPConfig.BASE_URL + page.find(**BOOKING_PAGE["security_code_img"]).get(
            "src"
        )

    @classmethod
    def parse_seat_prefer_value(cls, page: BeautifulSoup) -> str:
        options = page.find(**BOOKING_PAGE["seat_prefer_radio"])
        preferred_seat = options.find_next(selected="selected")
        return preferred_seat.attrs["value"]

    @classmethod
    def parse_types_of_trip_value(cls, page: BeautifulSoup) -> int:
        options = page.find(**BOOKING_PAGE["types_of_trip"])
        tag = options.find_next(selected="selected")
        return int(tag.attrs["value"])

    @classmethod
    def parse_search_by(cls, page: BeautifulSoup) -> str:
        candidates = page.find_all("input", {"name": "bookingMethod"})
        tag = next((cand for cand in candidates if "checked" in cand.attrs))
        return tag.attrs["value"]
