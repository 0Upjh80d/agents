from dataclasses import dataclass
from typing import Any, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    history: Optional[list] = None
    agent_name: Optional[str] = None
    user_info: Optional[dict] = None


@dataclass
class UserInfo:
    auth_header: Optional[dict] = None
    vaccine: Optional[str] = None
    clinic: Optional[str] = None
    data_type: Optional[str] = None
    date: str = "2025-03-01"  # str(date.today())
    restart: bool = False


class ChatResponse(BaseModel):
    agent_name: str
    history: Optional[list] = None
    data: Optional[Any] = None
    data_type: Optional[str] = None
    message: str
    user_info: dict


class BookingDetails(BaseModel):
    vaccine: str
    clinic: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
