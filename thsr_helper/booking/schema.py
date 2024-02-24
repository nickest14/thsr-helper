import re
from datetime import date, datetime
from typer import BadParameter
from pydantic import BaseModel, Field, validator

from .constants import Stations, ThsrTime


class BookingModel(BaseModel):
    start_station: int = Field(..., serialization_alias="selectStartStation")
    dest_station: int = Field(..., serialization_alias="selectDestinationStation")
    outbound_time: str = Field(..., serialization_alias="toTimeTable")
    outbound_date: str = Field(..., serialization_alias="toTimeInputField")
    adult_ticket_num: str = Field(
        "1F", serialization_alias="ticketPanel:rows:0:ticketAmount"
    )
    seat_prefer: str = Field(..., serialization_alias="seatCon:seatRadioGroup")
    types_of_trip: int = Field(..., serialization_alias="tripCon:typesoftrip")
    search_by: str = Field(..., serialization_alias="bookingMethod")
    class_type: int = Field(0, serialization_alias="trainCon:trainRadioGroup")
    security_code: str = Field(..., serialization_alias="homeCaptcha:securityCode")

    # TODO: Support other kind of ticket.
    # child_ticket_num: str = Field("0H", serialization_alias="ticketPanel:rows:1:ticketAmount")
    # disabled_ticket_num: str = Field("0W", serialization_alias="ticketPanel:rows:2:ticketAmount")
    # elder_ticket_num: str = Field("0E", serialization_alias="ticketPanel:rows:3:ticketAmount")
    # college_ticket_num: str = Field("0P", serialization_alias="ticketPanel:rows:4:ticketAmount")

    @validator("start_station", "dest_station")
    def check_station(cls, station):
        if station not in range(1, len(Stations) + 1):
            raise BadParameter(f"Unknown station number: {station}")
        return station

    @validator("outbound_time")
    def check_time(cls, time):
        if time not in ThsrTime.__members__.values():
            raise BadParameter(f"Unknown time: {time}")
        return time

    @validator("outbound_date")
    def check_date(cls, date_str):
        try:
            if matched := re.match(r"\d{8}", date_str):  # 20240101
                target_date = datetime.strptime(matched.string, "%Y%m%d").date()
            elif matched := re.match(
                r"\d{4}-[0]?\d+-[0]?\d+", date_str
            ):  # 2024-01-01, 2024-1-1
                target_date = datetime.strptime(matched.string, "%Y-%m-%d").date()
            elif matched := re.match(
                r"\d{4}/[0]?\d+/[0]?\d+", date_str
            ):  # 2024/01/01, 2024/10/1
                target_date = datetime.strptime(matched.string, "%Y/%m/%d").date()
            else:
                target_date = date.today()
            return target_date.strftime("%Y/%m/%d")
        except Exception:
            raise BadParameter(f"Unknown date format: {date_str}")

    @validator("adult_ticket_num")
    def check_adult_ticket_num(cls, value):
        if not re.match(r"\d+F", value):
            raise BadParameter(f"Invalid adult ticket num format: {value}")
        return value


class Train(BaseModel):
    id: int
    depart: str
    arrive: str
    travel_time: str
    discount_str: str
    form_value: str


class ConfirmTrainModel(BaseModel):
    selected_train: str = Field(
        ..., serialization_alias="TrainQueryDataViewPanel:TrainGroup"
    )


class ConfirmTicketModel(BaseModel):
    personal_id: str = Field(..., serialization_alias="dummyId")
    phone_num: str = Field(..., serialization_alias="dummyPhone")
    email: str = Field("", serialization_alias="email")
    member_radio: str = Field(
        ...,
        serialization_alias="TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup",
        description="非高鐵會員, 企業會員 / 高鐵會員 / 企業會員統編",
    )
    form_mark: str = Field("", serialization_alias="BookingS3FormSP:hf:0")
    id_input_radio: int = Field(
        0, serialization_alias="idInputRadio", description="0: 身份證字號 / 1: 護照號碼"
    )
    diff_over: int = Field(1, serialization_alias="diffOver")
    agree: str = Field("on", serialization_alias="agree")
    go_back_m: str = Field("", serialization_alias="isGoBackM")
    back_home: str = Field("", serialization_alias="backHome")
    tgo_error: int = Field(1, serialization_alias="TgoError")
    # TODO: Support early bird ticket
    early_bird: int = Field(0, serialization_alias="isEarlyBirdRegister")
    # passenger_count: int = Field(1, serialization_alias='passengerCount')
