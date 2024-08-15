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
            "User-Agent": HTTPConfig.HTTPHeader.USER_AGENT,
            "Accept": HTTPConfig.HTTPHeader.ACCEPT_HTML,
            "Accept-Language": HTTPConfig.HTTPHeader.ACCEPT_LANGUAGE,
            "Referer": HTTPConfig.HTTPHeader.REFERER,
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

    def booking_page(self) -> Response:
        return self.session.get(
            HTTPConfig.BOOKING_PAGE_URL,
            headers=self.common_header,
            allow_redirects=True,
            timeout=2,
        )

    def get_captcha_img(self, img_url: str) -> Response:
        return self.session.get(img_url, headers=self.common_header, timeout=2)

    def submit_booking_form(self, params: Mapping[str, Any]) -> Response:
        url = HTTPConfig.SUBMIT_FORM_URL.format(self.session.cookies["JSESSIONID"])
        return self.session.post(
            url,
            headers=self.common_header,
            params=params,
            allow_redirects=True,
            timeout=2,
        )

    def submit_train(self, params: Mapping[str, Any]) -> Response:
        return self.session.post(
            HTTPConfig.CONFIRM_TRAIN_URL,
            headers=self.common_header,
            params=params,
            allow_redirects=True,
            timeout=2,
        )

    def submit_ticket(self, params: Mapping[str, Any]) -> Response:
        return self.session.post(
            HTTPConfig.CONFIRM_TICKET_URL,
            headers=self.common_header,
            params=params,
            allow_redirects=True,
            timeout=2,
        )
