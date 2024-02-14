from typer import BadParameter
from pydantic import BaseModel, Field, validator

from .constants import StationMapping

class BookingModel(BaseModel):
    start_station: int = Field(..., serialization_alias='selectStartStation')
    dest_station: int = Field(..., serialization_alias='selectDestinationStation')
    search_by: str = Field(..., serialization_alias='bookingMethod')
    types_of_trip: int = Field(..., serialization_alias='tripCon:typesoftrip')
    outbound_date: str = Field(..., serialization_alias='toTimeInputField')
    outbound_time: str = Field(..., serialization_alias='toTimeTable')
    security_code: str = Field(..., serialization_alias='homeCaptcha:securityCode')
    seat_prefer: str = Field(..., serialization_alias='seatCon:seatRadioGroup')
    form_mark: str = Field('', serialization_alias='BookingS1Form:hf:0')
    class_type: int = Field(0, serialization_alias='trainCon:trainRadioGroup')
    inbound_date: str = Field(None, serialization_alias='backTimeInputField')
    inbound_time: str = Field(None, serialization_alias='backTimeTable')
    to_train_id: int = Field(None, serialization_alias='toTrainIDInputField')
    back_train_id: int = Field(None, serialization_alias='backTrainIDInputField')
    adult_ticket_num: str = Field('1F', serialization_alias='ticketPanel:rows:0:ticketAmount')
    child_ticket_num: str = Field('0H', serialization_alias='ticketPanel:rows:1:ticketAmount')
    disabled_ticket_num: str = Field('0W', serialization_alias='ticketPanel:rows:2:ticketAmount')
    elder_ticket_num: str = Field('0E', serialization_alias='ticketPanel:rows:3:ticketAmount')
    college_ticket_num: str = Field('0P', serialization_alias='ticketPanel:rows:4:ticketAmount')

    @validator('start_station', 'dest_station')
    def check_station(cls, station):
        if station not in range(1, len(StationMapping) + 1):
            raise BadParameter(f'Unknown station number: {station}')
        return station