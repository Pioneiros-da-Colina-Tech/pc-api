from datetime import datetime

from pydantic import BaseModel


class Meeting(BaseModel):
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    location: str | None = None
    attendees: list[str] = []
