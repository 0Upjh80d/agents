import json
import os
from dataclasses import dataclass
from typing import Optional

import httpx
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent
from services.openai.tools import (
    fetch_vaccination_history_tool,
    recommend_vaccines_tool,
)

from agents import (
    Agent,
    AgentUpdatedStreamEvent,
    OpenAIChatCompletionsModel,
    RawResponsesStreamEvent,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    handoff,
    set_tracing_disabled,
)

load_dotenv(dotenv_path=r"..\.env")

OPENAI_HOST = os.getenv("OPENAI_HOST", "azure")
OPENAI_CHATGPT_MODEL = os.getenv("AZURE_OPENAI_CHATGPT_MODEL")
AZURE_OPENAI_SERVICE = os.getenv("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION") or "2024-03-01-preview"
TEMPERATURE = 0.0
SEED = 1234

RESPONSE_TOKEN_LIMIT = 512
CHATGPT_TOKEN_LIMIT = 128000

set_tracing_disabled(True)

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
    vaccine_recommendations: Optional[str] = None
    enrolled_type: Optional[str] = None
    enrolled_name: Optional[str] = None
    date: str = "2025-03-01"  # str(date.today())
    restart: bool = False


general_questions_agent = Agent(
    name="general_questions_agent",
    instructions=(
        "You are tasked to answer the vaccination related query."
        "Answer in a concise manner that answers the user's questions."
        # "Use the answer generation tool provided to you. Only return response from the tool only and do not use your own knowledge."
    ),
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)

vaccination_records_agent = Agent[UserInfo](
    name="vaccination_records_agent",
    instructions=(
        """
    You are tasked with retrieving the records of the user.
    Use fetch_vaccination_history_tool to retrieve the records.
    Output the results.
    """
    ),
    tools=[fetch_vaccination_history_tool],
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)


# TODO: Enhanced recommendations: Add feature to also consider past records
recommender_agent = Agent[UserInfo](
    name="recommender_agent",
    instructions=(
        """
    You are tasked with giving vaccine recommendations for the user.
    Use the recommend_vaccines_tool to give vaccine recommendations to the user.
    Output the results.
    """
    ),
    tools=[recommend_vaccines_tool],
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a helpful assistant that directs user queries to the appropriate agents."
        "Take the conversation history as context when deciding who to handoff to next."
        "If they ask requests regarding vaccination appointments, handoff to appointments_agent."
        "If they ask for vaccination reccomendations, handoff to recommender_agent."
        "If they ask about vaccination records, like asking about their past vaccinations, handoff to vaccination_records_agent."
        "Otherwise, handoff to general_questions_agent."
    ),
    handoffs=[
        handoff(agent=recommender_agent),
        handoff(agent=vaccination_records_agent),
        handoff(agent=general_questions_agent),
    ],
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)


async def main(user_msg):
    user_data = {
        "username": "mark.johnson@example.net",
        "password": "password123",
    }  # No enrollment. Auth-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjI5NjdjMGEtNTEyMS00YzQ2LWE0ZGMtMmI3OTc5Y2ZiNDIxIiwicmVmcmVzaCI6ZmFsc2UsImV4cCI6MTc1MTYxMzI1MH0.ofK7WchfCkzxMnKpOGTQSUiaIH9NKviXhD6OtQns8Xk
    # user_data = {"username": "kimberly.garza@example.net", "password": "abc123"} # Enrolled in Polyclinic
    # user_data = {"username": "gabrielle.davis@example.com", "password": "guest"} # Enrolled in GP

    login_data = {
        "grant_type": "password",  # Required
        "username": user_data["username"],  # Email used for login
        "password": user_data["password"],  # Password used for login
        "scope": "",  # Optional (empty value sent)
        "client_id": "",  # Optional (empty value sent)
        "client_secret": "",  # Optional (empty value sent)
    }

    async with httpx.AsyncClient(timeout=10.0) as httpclient:
        try:
            login = await httpclient.post(
                "http://127.0.0.1:8000/login", data=login_data
            )
            print(login.status_code)
            print(login.json().get("detail"))
        except Exception as e:
            print(f"Error making request: {e}")

    response = json.loads(login.text)
    auth_token = response["access_token"]
    user_info = RunContextWrapper(
        context=UserInfo(
            auth_header={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json",
            }
        )
    )

    # Get enrollment
    async with httpx.AsyncClient(timeout=10.0) as httpclient:
        try:
            user_response = await httpclient.get(
                "http://127.0.0.1:8000/users", headers=user_info.context.auth_header
            )
            print(user_response.status_code)
            print(user_response.json().get("detail"))
        except Exception as e:
            print(f"Error making request: {e}")

    print(user_response.text)

    enrollment_type = json.loads(user_response.text)["enrolled_clinic"]
    if enrollment_type:
        user_info.context.enrolled_type = enrollment_type["type"]
        user_info.context.enrolled_name = enrollment_type["name"]

    agent = orchestrator_agent
    inputs: list[TResponseInputItem] = [{"content": user_msg, "role": "user"}]

    response = ""
    result = Runner.run_streamed(agent, input=inputs, context=user_info, max_turns=20)
    async for event in result.stream_events():
        print(f"Received event: {event}")
        if isinstance(event, RawResponsesStreamEvent):
            data = event.data
            print(f"Processing RawResponsesStreamEvent: {data}")
            if isinstance(data, ResponseTextDeltaEvent):
                response += data.delta
            elif isinstance(data, ResponseContentPartDoneEvent):
                response += "\n"
        elif isinstance(event, AgentUpdatedStreamEvent):
            print(f"Handoff occurred: {event}")

    print(response)

    inputs = result.to_input_list()
    print("\n")

    inputs.append({"content": user_msg, "role": "user"})

    return response
