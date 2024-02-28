from pydantic import BaseModel
from typing import List
from typing import Optional


class UserSettings(BaseModel):
    personal_id: str = ""
    phone_number: Optional[str] = None
    email: Optional[str] = None


class ConditionSettings(BaseModel):
    adult_ticket_num: Optional[int] = None
    adult_ids: Optional[str] = None
    child_ticket_num: Optional[int] = None
    disabled_ticket_num: Optional[int] = None
    disabled_ids: Optional[str] = None
    elder_ticket_num: Optional[int] = None
    elder_ids: Optional[str] = None
    college_ticket_num: Optional[int] = None
    train_requirement: str = "0"
    date: str = ""
    thsr_time: str = ""
    time_range: List[int] = [0, 24]
    start_station: str = ""
    dest_station: str = ""
