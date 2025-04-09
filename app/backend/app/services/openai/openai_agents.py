import json
import os
from dataclasses import asdict

import httpx
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent
from schemas.chat import ChatResponse, UserInfo
from services.openai.tools import (
    cancel_appointment_tool,
    fetch_vaccination_history_tool,
    get_available_slots_tool,
    get_clinic_name_response_helper_tool,
    new_appointment_tool,
    recommend_vaccines_tool,
    reschedule_appointment_tool,
    standardise_vaccine_name_tool,
)

from agents import (
    Agent,
    AgentUpdatedStreamEvent,
    OpenAIChatCompletionsModel,
    RawResponsesStreamEvent,
    RunContextWrapper,
    RunItemStreamEvent,
    Runner,
    ToolCallOutputItem,
    TResponseInputItem,
    set_tracing_disabled,
)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../../../.env"))

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


def check_available_slots_agent_prompt(
    context_wrapper: RunContextWrapper[UserInfo], agent: Agent[UserInfo]
) -> str:
    context: UserInfo = context_wrapper.context.context
    return f"""
        Follow the steps in order:
        1. **Gathering inputs for get_available_slots_tool**: Look at function call result from previous agent and use that as the polyclinic input.
        Look at chat history. If the user specified a date, use that as input to return slots for that date. Else, return slots from {context.date} to 3 days after.
        2. **Get slots from polyclinic**: Use the get_available_slots_tool to find available slots at the polyclinic.
        3. Handoff to appointments_agent.
        """


check_available_slots_agent = Agent(
    name="check_available_slots_agent",
    instructions=check_available_slots_agent_prompt,
    tools=[get_available_slots_tool],
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)

# TODO: Add validity check for polyclinic name
identify_clinic_agent = Agent(
    name="identify_clinic_agent",
    instructions=(
        """
        You are part of a team of agents handling vaccination booking.
        Your task in this team is to only look at chat history and extract from chat history the name of clinic user would like to get.
        Follow the steps in order:
        1. Give the clinic_name you found, or 'Not found' if no clinic name was specified as input to the get_clinic_name_response_helper_tool.
        3. If the tool output asks user to specify which clinic, ask the question from tool output to user and stop.
        4. Handoff to the check_available_slots_agent.
        """
    ),
    handoffs=[check_available_slots_agent],
    tools=[get_clinic_name_response_helper_tool],
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)

handle_vaccine_names_agent = Agent(
    name="handle_vaccine_names_agent",
    instructions=(
        "You are part of a team of agents handling vaccination booking."
        "Your task in this team is to only look at chat history and extract from chat history the vaccine type user would like to get."
        "Follow these steps in order:"
        "1. Find the vaccine name mentioned and Use the standardise_vaccine_name_tool to convert it to the official name."
        "2. If the tool output is a vaccine name, use its output and handoff to the identify_clinic_agent."
        "3. If the tool output asks to handoff to recommender_agent, handoff to the recommender_agent."
    ),
    handoffs=[identify_clinic_agent, recommender_agent],
    tools=[standardise_vaccine_name_tool],
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)

# TODO: Handle reschedule and cancellation
manage_appointment_agent = Agent(
    name="manage_appointment_agent",
    instructions=(
        "Your task is to complete actions the user would like regarding vaccination appointments."
        "For new bookings, use the new_appointment_tool. For cancellations, use the cancel_appointment_tool."
        "For rescheduling existing appointments, use the reschedule_appointment_tool."
        "Return the output from any toolcall."
    ),
    tools=[new_appointment_tool, cancel_appointment_tool, reschedule_appointment_tool],
    # handoffs=[check_available_slots_agent],
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)

# TODO: Check enhanced recommendations for checking eligibility
appointments_agent = Agent[UserInfo](
    name="appointments_agent",
    instructions=(
        """
    # System context\nYou are part of a multi-agent system called the Agents SDK, designed to make agent coordination and execution easy. Agents uses two primary abstraction: **Agents** and **Handoffs**. An agent encompasses instructions and tools and can hand off a conversation to another agent when appropriate. Handoffs are achieved by calling a handoff function, generally named `transfer_to_<agent_name>`. Transfers between agents are handled seamlessly in the background; do not mention or draw attention to these transfers in your conversation with the user.\n

    Your task is to decide which agent to handoff to. Use tools to handoff to other agents. Do not output any text to user.
    If the user wants to book a new slot, handoff to handle_vaccine_names_agent.
    If the user is asking about rescheduling or cancelling an existing booking: Handoff to the manage_appointment_agent to handle.
    """
    ),
    handoffs=[
        handle_vaccine_names_agent,  # starts flow to get location and vaccine name.
        manage_appointment_agent,
    ],
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)

# Add backlinks from sub-agents under 'bookings team'
check_available_slots_agent.handoffs.append(manage_appointment_agent)
# manage_appointment_agent.handoffs.append(appointments_agent)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a helpful assistant that directs user queries to the appropriate agents."
        "Take the conversation history as context when deciding who to handoff to next."
        "If they want to book vaccination appointments, but did not mention which vaccine they want, handoff to the recommender_agent."
        "If they mentioned their desired vaccine and would like to book an appointment, handoff to appointments_agent."
        "If they ask for vaccination reccomendations, handoff to recommender_agent."
        "If they ask about vaccination records, like asking about their past vaccinations, handoff to vaccination_records_agent."
        "Otherwise, handoff to general_questions_agent."
    ),
    handoffs=[
        appointments_agent,
        recommender_agent,
        vaccination_records_agent,
        general_questions_agent,
    ],
    model=OpenAIChatCompletionsModel(model="chat", openai_client=client),
)


async def main(
    user_msg: str,
    history: list | None,
    current_agent: str | None,
    user_info: dict | None,
) -> ChatResponse:

    # If received user_info context, init new wrapper with it for next run. Else create new.
    if user_info:
        user_info = UserInfo(**user_info)
        wrapper = RunContextWrapper(context=user_info)
    else:
        # Mock login
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
            except Exception as e:
                print(f"Error making request: {e}")

        response = json.loads(login.text)
        auth_token = response["access_token"]
        wrapper = RunContextWrapper(
            context=UserInfo(
                auth_header={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json",
                }
            )
        )

    # Init entry point agent
    if current_agent:
        current_agent_mapping = {
            "orchestrator_agent": orchestrator_agent,
            "appointments_agent": appointments_agent,
            "handle_vaccine_names_agent": handle_vaccine_names_agent,
            "identify_clinic_agent": identify_clinic_agent,
            "check_available_slots_agent": check_available_slots_agent,
        }
        agent = current_agent_mapping[current_agent]
    else:
        agent = orchestrator_agent

    # If have exsting history, append new user message to it, else create new
    if history:
        history.append({"content": user_msg, "role": "user"})
    else:
        history: list[TResponseInputItem] = [{"content": user_msg, "role": "user"}]

    # Always init
    tool_output = None
    final_agents = {
        "general_questions_agent",
        "vaccination_records_agent",
        "recommender_agent",
        "manage_appointment_agent",
    }
    message = ""

    # Iterate through runner events
    result = Runner.run_streamed(agent, input=history, context=wrapper, max_turns=20)
    async for event in result.stream_events():
        if isinstance(event, RawResponsesStreamEvent):
            data = event.data
            if isinstance(data, ResponseTextDeltaEvent):
                message += data.delta
            elif isinstance(data, ResponseContentPartDoneEvent):
                message += "\n"
        elif isinstance(event, AgentUpdatedStreamEvent):
            print(f"Handoff occurred: {event}")
        elif isinstance(event, RunItemStreamEvent):
            if isinstance(event.item, ToolCallOutputItem):
                if event.item.agent.name in {
                    "recommender_agent",
                    "vaccination_records_agent",
                    "handle_vaccine_names_agent",
                    "identify_clinic_agent",
                    "check_available_slots_agent",
                    "manage_appointment_agent",
                }:
                    tool_output = event.item.output
    print(message)

    history = result.to_input_list()
    print("\n")

    current_agent = result.current_agent.name
    # If current agent is one of the final_agents, or restart flag set to True, change current agent to orchestrator
    if current_agent in final_agents or wrapper.context.restart:
        current_agent = "orchestrator_agent"
        wrapper.context.restart = False

    # TODO: handle cases where halfmade booking cache should be removed

    response_dict = {
        "message": message,
        "data": tool_output,
        "history": history,
        "agent_name": current_agent,
        "data_type": wrapper.context.data_type,
        "user_info": asdict(wrapper.context),
    }

    response = ChatResponse(**response_dict)

    return response
