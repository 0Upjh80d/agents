from fastapi import APIRouter
from schemas.chat import ChatRequest, ChatResponse
from services.openai import openai_agents

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_chat(chat_request: ChatRequest):
    print("Received chat request:", chat_request.message)
    response: ChatResponse = await openai_agents.main(
        user_msg=chat_request.message,
        history=chat_request.history,
        current_agent=chat_request.agent_name,
        user_info=chat_request.user_info,
    )
    return response
