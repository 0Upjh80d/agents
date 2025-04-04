from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/dummy_orchestrator", tags=["dummy_orchestrator"])


class OrchestratorResponse(BaseModel):
    agent_name: str
    data_type: str
    data: dict
    message: str


@router.get("", response_model=OrchestratorResponse)
async def dummy_orchestrator():
    response = OrchestratorResponse(
        agent_name="Orchestrator Agent",
        data_type="vaccine_record",
        data={
            "vaccines": [
                "Influenza (INF)",
                "Pneumococcal Conjugate (PCV13)",
                "Human Papillomavirus (HPV)",
                "Tetanus, Diphtheria, Pertussis (Tdap)",
                "Hepatitis B (HepB)",
                "Measles, Mumps, Rubella (MMR)",
                "Varicella (VAR)",
            ]
        },
        message="This is a dummy response from the orchestrator.",
    )
    return response
