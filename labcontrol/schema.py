from datetime import datetime, timedelta
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SeleniumCookie(BaseModel):
    # https://www.selenium.dev/selenium/docs/api/javascript/Options.Cookie.html
    name: str
    value: str
    domain: str
    expiry: int = Field(
        default=0,
        description="Unix timestamp en segundos. El valor cero indica que la cookies ya expiro o no se debe agregar al navegador.",
    )
    httpOnly: bool = False
    path: str = "/"
    sameSite: str = "None"
    secure: bool = False


class AWSDetails(BaseModel):
    session_started_at: Optional[datetime]
    session_status: str
    session_status_time: datetime
    accumulated_lab_time: timedelta


class AWSAction(Enum):
    getawsstatus = "getawsstatus"  # Devuelve el status del lab.
    getaws = "getaws"
    startaws = "startaws"
    endaws = "endaws"


class VocareumParams(BaseModel):
    stepid: int
    vockey: str
    version: Literal["0"] = "0"
    mode: Literal["s"] = "s"
    type: Literal["1"] = "1"


class AWSStatusSuccess(BaseModel):
    success: Literal[True]
    status: str


class AWSStatusFailure(BaseModel):
    success: Literal[False]
    error: str


class LoginSuccess(BaseModel):
    success: Literal[True]
    cookies: List["SeleniumCookie"]


class LoginFailure(BaseModel):
    success: Literal[False]
    error: str


AWSStatus = AWSStatusSuccess | AWSStatusFailure
Login = LoginSuccess | LoginFailure
