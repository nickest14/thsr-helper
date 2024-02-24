import re
from typing import Tuple
from typer import BadParameter


def validate_personal_id(value: str):
    pattern = r"^[a-zA-Z][0-9]{9}$"
    if value and not re.match(pattern, value):
        raise BadParameter(
            "Personal ID must start with an English character and be exactly 10 characters long."
        )
    return value


def validate_phone_number(value: str):
    pattern = r"^09[0-9]{8}$"
    if value and not re.match(pattern, value):
        raise BadParameter(
            "Phone number must begin with the digits '09' and be exactly 10 characters long."
        )
    return value


def validate_email(value: str):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if value and not re.match(pattern, value):
        raise BadParameter("Wrong email format.")
    return value


def validate_time_range(value: Tuple[int, int]):
    start_hour, end_hour = value
    if start_hour and end_hour:
        if not start_hour <= end_hour:
            raise BadParameter("End hour must be greater than or equal to start hour.")
    return value
