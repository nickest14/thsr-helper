
from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import Response

from .constants import HTTPConfig
from .parser import parse_captcha_img_url

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

    def get_captcha_img(self, book_page: bytes) -> Response:
        img_url = parse_captcha_img_url(book_page)
        return self.session.get(img_url, headers=self.common_header)
