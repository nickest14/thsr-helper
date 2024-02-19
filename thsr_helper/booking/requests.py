from typing import Mapping, Any

from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import Response

from .constants import HTTPConfig

class HTTPRequest:
    def __init__(self, max_retries: int = 3) -> None:
        self.session = Session()
        self.session.mount("https://", HTTPAdapter(max_retries=max_retries))
        self.common_header: dict = {
            "Host": HTTPConfig.HTTPHeader.BOOKING_PAGE_HOST,
            "User-Agent": HTTPConfig.HTTPHeader.USER_AGENT,
            "Accept": HTTPConfig.HTTPHeader.ACCEPT_HTML,
            "Accept-Language": HTTPConfig.HTTPHeader.ACCEPT_LANGUAGE,
            "Accept-Encoding": HTTPConfig.HTTPHeader.ACCEPT_ENCODING,
        }

    def booking_page(self) -> Response:
        return self.session.get(HTTPConfig.BOOKING_PAGE_URL, headers=self.common_header, allow_redirects=True)

    def get_captcha_img(self, img_url: str) -> Response:
        return self.session.get(img_url, headers=self.common_header)

    def submit_booking_form(self, params: Mapping[str, Any]) -> Response:
        url = HTTPConfig.SUBMIT_FORM_URL.format(self.session.cookies["JSESSIONID"])
        return self.session.post(url, headers=self.common_header, params=params, allow_redirects=True)
