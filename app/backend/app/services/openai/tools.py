import json
import os
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional

import httpx
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletion
from openai_messages_token_helper import build_messages

from agents import (
    RunContextWrapper,
    function_tool,
)

# TODO: change this
load_dotenv(dotenv_path=r"..\..\..\..\..\.env")
OPENAI_HOST = os.getenv("OPENAI_HOST", "azure")
OPENAI_CHATGPT_MODEL = os.getenv("AZURE_OPENAI_CHATGPT_MODEL")
AZURE_OPENAI_SERVICE = os.getenv("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION") or "2024-03-01-preview"
TEMPERATURE = 0.0
SEED = 1234

RESPONSE_TOKEN_LIMIT = 512
CHATGPT_TOKEN_LIMIT = 128000

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    credential, "https://cognitiveservices.azure.com/.default"
)


client = AsyncAzureOpenAI(
    api_version="2024-10-21",
    azure_endpoint=f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com",
    azure_ad_token_provider=token_provider,
    azure_deployment=AZURE_OPENAI_CHATGPT_DEPLOYMENT,
)


@dataclass
class UserInfo:
    auth_header: Optional[dict] = None
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
    recommendations = json.loads(recommendations.text)
    return recommendations


@function_tool
async def standardise_vaccine_name_tool(
    wrapper: RunContextWrapper[UserInfo], requested_vaccine: str
) -> str:
    """
    Always call this tool.

    Args:
        requested_vaccine: Raw user input of vaccine type found from chat history (if any)
    """

    standard_name_prompt = f"""
    Find the closest match of {requested_vaccine} to the list below:
    - Influenza (INF)
    - Pneumococcal Conjugate (PCV13)
    - Human Papillomavirus (HPV)
    - Tetanus, Diphtheria, Pertussis (Tdap)
    - Hepatitis B (HepB)
    - Measles, Mumps, Rubella (MMR)
    - Varicella (VAR)

    If there is a match, return the value in the list exactly.
    Else, return "None"
    """

    messages = build_messages(
        model=OPENAI_CHATGPT_MODEL,
        system_prompt=standard_name_prompt,
        max_tokens=CHATGPT_TOKEN_LIMIT - RESPONSE_TOKEN_LIMIT,
    )

    chat_completion: ChatCompletion = await client.chat.completions.create(
        model=AZURE_OPENAI_CHATGPT_DEPLOYMENT,
        messages=messages,
        temperature=0,
        max_tokens=RESPONSE_TOKEN_LIMIT,
        n=1,
        stream=False,
        seed=SEED,
    )

    return chat_completion.choices[0].message.content


# TODO: In future change tool to get frontend to display vaccines list
@function_tool
async def clarify_vaccination_type_tool(wrapper: RunContextWrapper[UserInfo]) -> str:
    """
    Use this tool when the output from standardise_vaccine_name_tool is None.
    """
    return """
    "Please clarify which vaccine type you would like to take, choose from this list:
            - Influenza (INF)
            - Pneumococcal Conjugate (PCV13)
            - Human Papillomavirus (HPV)
            - Tetanus, Diphtheria, Pertussis (Tdap)
            - Hepatitis B (HepB)
            - Measles, Mumps, Rubella (MMR)
            - Varicella (VAR)"
    """


@function_tool
async def clinic_type_response_helper_tool(
    wrapper: RunContextWrapper[UserInfo], clinic_type_option: str
) -> str:

    # Decides response depending on whether clinic type could be extracted from chat history,
    # and what extracted type it is.
    """
    Always use this tool when the step requires it. This tool must be called first.

    Args:
        clinic_type_option: Takes either 'GP', 'Polyclinic' or 'Not mentioned'
    """
    context: UserInfo = wrapper.context.context
    if clinic_type_option == "Not mentioned":
        if context.enrolled_type:
            return context.enrolled_type
        return "Ask user to specify which type of clinic they want to visit, either GP or Polyclinic."
    return clinic_type_option


@function_tool
async def get_clinic_name_response_helper_tool(
    wrapper: RunContextWrapper[UserInfo], polyclinic_name: str, clinic_type_option: str
):

    # Decides response depending on whether polyclinic name could be extracted from chat history.
    """
    Always use this tool when the step requires it.

    Args:
        polyclinic_name: Takes either the polyclinic name or 'Not found'
    """
    context: UserInfo = wrapper.context.context
    enrolled_name = context.enrolled_name

    # If GP clinic, tell user to book from website instead. Recommend GP clinics near home if not enrolled in any. Go back to orchestrator agent.
    if clinic_type_option == "GP":
        context.restart = True

        if context.enrolled_name:
            return f"Tell user: 'You are enrolled under the GP clinic: {context.enrolled_name}. Please proceed to book slots there at: https://book.health.gov.sg/'"
        try:
            async with httpx.AsyncClient(timeout=10.0) as httpclient:
                get_recommended_gp = await httpclient.get(
                    url="http://127.0.0.1:8000/clinic/nearest",
                    headers=wrapper.context.context.auth_header,
                    params={
                        "clinic_type": "gp",
                        "clinic_limit": 3,
                    },
                )
        except Exception as e:
            print(f"Error making request: {e}")
        recommended_clinics = json.loads(get_recommended_gp.text)
        return f"Tell user: 'Here are your GP clinics near your home: {recommended_clinics}. Please proceed to book slots at: https://book.health.gov.sg/'"

    # If type is polyclinic but name not found in chat history, use enrolled polyclinic, if not enrolled then recommend polyclinics near home
    if polyclinic_name == "Not found":
        if enrolled_name:
            return f"Find slots at {enrolled_name}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as httpclient:
                get_recommended_polyclinic = await httpclient.get(
                    url="http://127.0.0.1:8000/clinic/nearest",
                    headers=wrapper.context.context.auth_header,
                    params={
                        "clinic_type": "polyclinic",
                        "clinic_limit": 3,
                    },
                )
        except Exception as e:
            print(f"Error making request: {e}")
        recommended_polyclinics = json.loads(get_recommended_polyclinic.text)
        return f"Please specify the polyclinic you want to book at. Here are some polyclinics nearer your home: {recommended_polyclinics}"
    return f"Find slots at {polyclinic_name}"


@function_tool
async def get_available_slots_tool(
    wrapper: RunContextWrapper[UserInfo],
    vaccine_name: str,
    polyclinic: str,
    start_date: date,
    end_date: date,
) -> List[Dict]:
    """
    Get available slots for a vaccine at a specific polyclinic, over a date ranges.

    Args:
        vaccine_name: Official name of vaccine type
        polyclinic: The name of polyclinic
        start_date: Start date of date range to search
        end_date: End date of date range to search
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as httpclient:
            get_slots = await httpclient.get(
                url="http://127.0.0.1:8000/bookings/available",
                headers=wrapper.context.context.auth_header,
                params={
                    "vaccine_name": vaccine_name,
                    "polyclinic_name": polyclinic,
                    "start_date": start_date,
                    "end_date": end_date,
                    "timeslot_limit": 6,
                },
            )
    except Exception as e:
        print(f"Error making request: {e}")
    result = json.loads(get_slots.text)
    return result


@function_tool
async def new_appointment_tool(
    wrapper: RunContextWrapper[UserInfo], slot_id: str
) -> str:
    """
    Handles booking of a new appointment.

    Args:
        slot_id: The 'id' field for slot to be booked
    """
    booking = {"booking_slot_id": slot_id}
    try:
        async with httpx.AsyncClient(timeout=10.0) as httpclient:
            book = await httpclient.post(
                url="http://127.0.0.1:8000/bookings/schedule",
                json=booking,
                headers=wrapper.context.context.auth_header,
            )
        status = book.status_code
        if status == 201:
            return "Successfully booked!"
    except Exception as e:
        print(f"Error making request: {e}")


@function_tool
async def reschedule_appointment_tool(  # TODO: Wait for UI?
    wrapper: RunContextWrapper[UserInfo],
    # record_id: int,
    # new_slot_id: int,
) -> int:
    """
    Handles rescheduling of an existing appointment.

    """
    # Args:
    #     user_id (int): The id for user
    #     record_id (int): The id for the vaccine_record to remove
    #     new_slot_id (int): The id of slot to reschedule a current slot to
    # """
    # Cancel the old appointment
    # cancel = requests.delete(
    #     url=f"http://127.0.0.1:8000/bookings/cancel/{record_id}"
    # )

    # # Book the new slot (does not check for avaialability currently)
    # booking = {"user_id": user_id, "booking_slot_id": new_slot_id}
    # book = requests.post(url="http://127.0.0.1:8000/bookings/schedule", json=booking)
    # return book.status_code
    return "Rescheduled Successfully"  # For testing only


@function_tool
async def cancel_appointment_tool(
    wrapper: RunContextWrapper[UserInfo], slot_id: int
) -> int:
    """
    Handles rescheduling of an existing appointment.
    """
    # Args:
    #     slot_id (int): The id for the slot to take action on
    # """
    # # Cancel the old appointment
    # cancel = requests.post(
    #     url=f"http://127.0.0.1:8000/bookings/cancel/{slot_id}"
    # )
    # return cancel.status_code
    return "Cancelled Successfully"
