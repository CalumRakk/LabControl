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


class AWSDetailsStopped(BaseModel):
    session_started_at: Optional[datetime]
    session_status: str
    session_status_time: datetime
    accumulated_lab_time: timedelta


class AWSDetailsRunning(BaseModel):
    copy_and_paste_credentials: str
    remaining_session_time: timedelta
    session_started_at: datetime
    session_to_end: datetime
    accumulated_lab_time: timedelta
    aws_sso: str


class AWSAction(Enum):
    getawsstatus = "getawsstatus"  # Devuelve el status del lab.
    getaws = "getaws"
    startaws = "startaws"
    endaws = "endaws"
    ssodownloadaws = "ssodownloadaws"


class LabStatus(Enum):
    stopped = "stopped"
    in_creation = "in creation"
    ready = "ready"


class VocareumParams(BaseModel):
    stepid: int
    vockey: str
    version: Literal["0"] = "0"
    mode: Literal["s"] = "s"
    type: Literal["1"] = "1"


class AWSStatusSuccess(BaseModel):
    success: Literal[True]
    status: LabStatus


class AWSStatusFailure(BaseModel):
    success: Literal[False]
    error: str


class LoginSuccess(BaseModel):
    success: Literal[True]
    cookies: List["SeleniumCookie"]


class LoginFailure(BaseModel):
    success: Literal[False]
    error: str


class AWSContentSuccess(BaseModel):
    success: Literal[True]
    content: str


class AWSContentFailure(BaseModel):
    success: Literal[False]
    error: str


class AWSStartSuccess(BaseModel):
    success: Literal[True]
    content: dict


class AWSStartFailure(BaseModel):
    success: Literal[False]
    error: str


class AWSEndSuccess(BaseModel):
    success: Literal[True]
    content: dict


class AWSEndFailure(BaseModel):
    success: Literal[False]
    error: str


AWSEnd = AWSEndSuccess | AWSEndFailure
AWSStart = AWSStartSuccess | AWSStartFailure
AWSContent = AWSContentSuccess | AWSContentFailure
AWSStatus = AWSStatusSuccess | AWSStatusFailure
Login = LoginSuccess | LoginFailure
