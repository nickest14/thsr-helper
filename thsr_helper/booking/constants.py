from enum import Enum, unique

class HTTPConfig:
    BASE_URL = "https://irs.thsrc.com.tw"
    BOOKING_PAGE_URL = "https://irs.thsrc.com.tw/IMINT/?locale=tw"
    SUBMIT_FORM_URL = "https://irs.thsrc.com.tw/IMINT/;jsessionid={}?wicket:interface=:0:BookingS1Form::IFormSubmitListener"
    CONFIRM_TRAIN_URL = "https://irs.thsrc.com.tw/IMINT/?wicket:interface=:1:BookingS2Form::IFormSubmitListener"
    CONFIRM_TICKET_URL = "https://irs.thsrc.com.tw/IMINT/?wicket:interface=:2:BookingS3Form::IFormSubmitListener"

    class HTTPHeader:
        BOOKING_PAGE_HOST = "irs.thsrc.com.tw"
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        ACCEPT_HTML = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        )
        ACCEPT_IMG = "image/webp,*/*"
        ACCEPT_LANGUAGE = "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3"
        ACCEPT_ENCODING = "gzip, deflate, br"

class StationMapping(Enum):
    Nangang = 1
    Taipei = 2
    Banqiao = 3
    Taoyuan = 4
    Hsinchu = 5
    Miaoli = 6
    Taichung = 7
    Changhua = 8
    Yunlin = 9
    Chiayi = 10
    Tainan = 11
    Zuouing = 12

@unique
class ThsrTime(str, Enum):
    A1201 = "1201A"
    A1230 = "1230A"
    A600 = "600A"
    A630 = "630A"
    A700 = "700A"
    A730 = "730A"
    A800 = "800A"
    A830 = "830A"
    A900 = "900A"
    A930 = "930A"
    A1000 = "1000A"
    A1030 = "1030A"
    A1100 = "1100A"
    A1130 = "1130A"
    N1200 = "1200N"
    P1230 = "1230P"
    P100 = "100P"
    P130 = "130P"
    P200 = "200P"
    P230 = "230P"
    P300 = "300P"
    P330 = "330P"
    P400 = "400P"
    P430 = "430P"
    P500 = "500P"
    P530 = "530P"
    P600 = "600P"
    P630 = "630P"
    P700 = "700P"
    P730 = "730P"
    P800 = "800P"
    P830 = "830P"
    P900 = "900P"
    P930 = "930P"
    P1000 = "1000P"
    P1030 = "1030P"
    P1100 = "1100P"
    P1130 = "1130P"