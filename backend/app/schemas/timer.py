from pydantic import BaseModel
from typing import Literal
from typing import Optional
from datetime import datetime

class TimerStartRequest(BaseModel):
    duration: int
    type: Literal["pomodoro", "break"]

class TimerStartResponse(BaseModel):
    sessionId: int
    status: str

class TimerStopRequest(BaseModel):
    sessionId: int

class TimerStopResponse(BaseModel):
    status: str
    timeSpent: int

class TimerStatusRequest(BaseModel):
    sessionId: int

class TimerStatusResponse(BaseModel):
    status: str
    remainingTime: int

class StudySessionCreate(BaseModel):
    duration: int  # в минутах
    type: str  # например, "pomodoro"

class StudySessionOut(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    duration: int
    type: str

    class Config:
        orm_mode = True