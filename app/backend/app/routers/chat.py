from fastapi import APIRouter

from app.backend.app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_chat(chat_request: ChatRequest):
    print("Received chat request:", chat_request.text)
    response = ChatResponse(text="Hello")
    return response
