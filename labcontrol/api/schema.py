from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

class AWSDetails(BaseModel):
    session_started_at: Optional[datetime]
    session_status: str
    session_status_time: datetime
    accumulated_lab_time: timedelta