from typing import Mapping, Any

from bs4 import BeautifulSoup

from .constants import HTTPConfig

BOOKING_PAGE: Mapping[str, Any] = {
    "security_code_img": {
        "id": "BookingS1Form_homeCaptcha_passCode"
    },
}

def html_to_soup(content: bytes) -> BeautifulSoup:
    return BeautifulSoup(content, features="html.parser")

def parse_captcha_img_url(html: bytes) -> str:
    page = html_to_soup(html)
    return HTTPConfig.BASE_URL + page.find(**BOOKING_PAGE["security_code_img"]).get('src')

