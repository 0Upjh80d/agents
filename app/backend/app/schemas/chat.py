from typing import Any, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    history: Optional[list] = None
    agent_name: Optional[str] = None


class ChatResponse(BaseModel):
    agent_name: str
    history: Optional[list] = None
    data: Optional[Any] = None
    message: str
