from datetime import datetime
from pydantic import BaseModel


class AWSDetails(BaseModel):
    session_started_at: datetime
    session_status: str
    session_status_time: datetime
    accumulated_lab_time: str
