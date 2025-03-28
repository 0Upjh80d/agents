from typing import List

from autogen_core.models import (
    LLMMessage,
)
from pydantic import BaseModel

# UserLogin is a message published by the runtime when a user logs in and starts a new session.


class UserLogin(BaseModel):
    pass


# UserTask is a message containing the chat history of the user session.
# When an AI agent hands off a task to other agents, it also publishes a UserTask message.


class UserTask(BaseModel):
    context: List[LLMMessage]


# AgentResponse is a message published by the AI agents and the Human Agent,
# it also contains the chat history as well as a topic type for the customer to reply to.


class AgentResponse(BaseModel):
    reply_to_topic_type: str
    context: List[LLMMessage]
