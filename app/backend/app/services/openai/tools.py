import json
from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx
from dotenv import load_dotenv

from agents import (
    RunContextWrapper,
    function_tool,
)

# TODO: change this
load_dotenv(dotenv_path=r"..\..\..\..\..\.env")


@dataclass
class UserInfo:
    auth_header: Optional[dict] = None
    vaccine_recommendations: Optional[str] = None
    enrolled_type: Optional[str] = None
    enrolled_name: Optional[str] = None
    date: str = "2025-03-01"  # str(date.today())
    restart: bool = False


# Tools
@function_tool
async def fetch_vaccination_history_tool(
    wrapper: RunContextWrapper[UserInfo],
) -> List[Dict]:
    """
    Get user's past vaccinations.
    """
    async with httpx.AsyncClient(timeout=10.0) as httpclient:
        try:
            vaccination_history_records = await httpclient.get(
                "http://127.0.0.1:8000/records",
                headers=wrapper.context.context.auth_header,
            )
        except Exception as e:
            print(f"Error making request: {e}")
    vaccination_history_records = json.loads(vaccination_history_records.text)
    return vaccination_history_records


@function_tool
async def recommend_vaccines_tool(wrapper: RunContextWrapper[UserInfo]) -> str:
    """
    Get vaccine recommendations for user.
    """
    async with httpx.AsyncClient(timeout=10.0) as httpclient:
        try:
            recommendations = await httpclient.get(
                "http://127.0.0.1:8000/vaccines/recommendations",
                headers=wrapper.context.context.auth_header,
            )
        except Exception as e:
            print(f"Error making request: {e}")
    wrapper.context.context.vaccine_recommendations = recommendations.text
    return recommendations.text
