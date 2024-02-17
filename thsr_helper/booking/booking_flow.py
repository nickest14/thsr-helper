from typing import Tuple
import json

from requests.models import Response
from .utils import fill_code
from .parser import html_to_soup
from .schema import BookingModel
from thsr_helper.booking.requests import HTTPRequest

class BookingFlow:
    def __init__(self) -> None:
        self.client = HTTPRequest()

    def run(self) -> None:
        InitPageFlow(self.client).run()


class InitPageFlow():
    def __init__(self, client: HTTPRequest) -> None:
        self.client = client

    def run(self) -> Tuple[Response, int]:
        book_page: bytes = self.client.booking_page().content
        img: bytes = self.client.get_captcha_img(book_page).content
        security_code = fill_code(img, manual=False)
        page = html_to_soup(book_page)
        # TODO: Add BookingModel


