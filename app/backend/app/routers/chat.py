from fastapi import APIRouter
from schemas.chat import ChatRequest, ChatResponse
from services.openai import openai_agents

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_chat(chat_request: ChatRequest):
    print("Received chat request:", chat_request.text)
    response_text = await openai_agents.main(user_msg=chat_request.text)
    response = ChatResponse(text=response_text)
    return response
