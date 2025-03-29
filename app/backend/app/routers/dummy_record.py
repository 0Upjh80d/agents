from fastapi import APIRouter
from schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/dummy_record", tags=["dummy_record"])


@router.post("", response_model=ChatResponse)
async def send_dummy_record(chat_request: ChatRequest):
    print("Received chat request:", chat_request.text)
    response = ChatResponse(
        text="Influenza (INF), Pneumococcal Conjugate (PCV13), Human Papillomavirus (HPV), Tetanus, Diphtheria , Pertussis (Tdap), Hepatitis B (HepB), Measles, Mumps, Rubella (MMR), Varicella (VAR)")
    return response
