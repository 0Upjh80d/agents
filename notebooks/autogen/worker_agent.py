import datetime
import json
import pprint
from typing import List, Tuple

from agent_tools import (
    get_user_details,
)
from agent_tools_wrapper import (
    cancel_booking_tool,
    get_available_booking_slots_tool,
    get_nearest_polyclinic_tool,
    get_vaccination_history_tool,
    get_vaccine_recommendations_tool,
    schedule_vaccination_slot_tool,
    transfer_back_to_triage_tool,
    transfer_to_appointment_agent_tool,
    transfer_to_recommender_agent_tool,
    transfer_to_vaccine_records_agent_tool,
)

# testing openai connection
from autogen_core import (
    FunctionCall,
    MessageContext,
    RoutedAgent,
    TopicId,
    TypeSubscription,
    message_handler,
)
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    FunctionExecutionResult,
    FunctionExecutionResultMessage,
    SystemMessage,
)
from autogen_core.tools import Tool

# Message types
from message_type import AgentResponse, UserTask
from pydantic import BaseModel


class UserDetails(BaseModel):
    address: str
    created_at: str
    date_of_birth: str
    email: str
    enrolled_clinic: str
    first_name: str
    gender: str
    last_name: str
    nric: str
    updated_at: str


pp = pprint.PrettyPrinter(indent=4)


# These tools can be passed to an agent system to be executed or used by other agents.
# description parameter provides context for how the tool should be used.

# define the topic types each of the agents will subscribe to
vaccine_records_topic_type = "VaccineRecordsAgent"
vaccine_recommendation_topic_type = "VaccineRecommenderAgent"
appointment_topic_type = "AppointmentAgent"
triage_agent_topic_type = "TriageAgent"
user_topic_type = "User"  # HealthHub AI


class AIAgent(RoutedAgent):
    def __init__(
        self,
        description: str,
        system_message: SystemMessage,
        model_client: ChatCompletionClient,
        tools: List[Tool],
        delegate_tools: List[Tool],
        agent_topic_type: str,
        user_topic_type: str,
        access_token: str = None,
        user_details: UserDetails = None,
    ) -> None:
        super().__init__(description)
        self._system_message = system_message
        self._model_client = model_client
        self._tools = dict([(tool.name, tool) for tool in tools])
        self._tool_schema = [tool.schema for tool in tools]
        self._delegate_tools = dict([(tool.name, tool) for tool in delegate_tools])
        self._delegate_tool_schema = [tool.schema for tool in delegate_tools]
        self._agent_topic_type = agent_topic_type
        self._user_topic_type = user_topic_type
        self._user_details = user_details
        self._user_detail_message = None

    @message_handler
    async def handle_task(self, message: UserTask, ctx: MessageContext) -> None:
        # retrieve user details
        self._user_details = get_user_details()
        user_detail_message_context = "Current logged in user's detail: " + str(
            get_user_details()
        )

        # append current date and time
        user_detail_and_date_message_context = (
            user_detail_message_context
            + "\nToday's date and time: "
            + str(datetime.datetime.now())
            + "\n"
        )

        # Send the task to the LLM.
        llm_result = await self._model_client.create(
            messages=[
                SystemMessage(
                    content=user_detail_and_date_message_context, source=self.id.type
                )
            ]  # Wrap SystemMessage in a list
            + [self._system_message]
            + message.context,
            tools=self._tool_schema + self._delegate_tool_schema,
            cancellation_token=ctx.cancellation_token,
        )
        print(f"{'-'*80}\n{self.id.type}:", flush=True)
        if isinstance(llm_result.content, list):
            print(
                f"[LOGGING] number of tools to be performed: {len(llm_result.content) if isinstance(llm_result.content, list) else "NA"}",
                flush=True,
            )

        if isinstance(llm_result.content, list):
            # print("llm_reselt.content:", end="")
            for fun in llm_result.content:
                print(fun, flush=True)
        else:
            print(llm_result.content, flush=True)

        # Process the LLM result.
        while isinstance(llm_result.content, list) and all(
            isinstance(m, FunctionCall) for m in llm_result.content
        ):
            tool_call_results: List[FunctionExecutionResult] = []
            delegate_targets: List[Tuple[str, UserTask]] = []
            # Process each function call.
            for call in llm_result.content:
                arguments = json.loads(call.arguments)

                if call.name in self._tools:
                    # Execute the tool directly.
                    result = await self._tools[call.name].run_json(
                        arguments, ctx.cancellation_token
                    )
                    result_as_str = self._tools[call.name].return_value_as_string(
                        result
                    )
                    tool_call_results.append(
                        FunctionExecutionResult(
                            call_id=call.id,
                            content=result_as_str,
                            is_error=False,
                            name=call.name,
                        )
                    )

                elif call.name in self._delegate_tools:
                    # Execute the tool to get the delegate agent's topic type.
                    result = await self._delegate_tools[call.name].run_json(
                        arguments, ctx.cancellation_token
                    )
                    topic_type = self._delegate_tools[call.name].return_value_as_string(
                        result
                    )
                    # Create the context for the delegate agent, including the function call and the result.
                    delegate_messages = list(message.context) + [
                        AssistantMessage(content=[call], source=self.id.type),
                        FunctionExecutionResultMessage(
                            content=[
                                FunctionExecutionResult(
                                    call_id=call.id,
                                    content=f"Transferred to {topic_type}. Adopt persona immediately."
                                    "Read through the context and capture the details of the ongoing task, then carry on on with the task diligently.",
                                    is_error=False,
                                    name=call.name,
                                )
                            ]
                        ),
                    ]
                    delegate_targets.append(
                        (topic_type, UserTask(context=delegate_messages))
                    )
                else:
                    raise ValueError(f"Unknown tool: {call.name}")

            if len(delegate_targets) > 0:
                assert (
                    len(delegate_targets) == 1
                ), f"There should be only 1 delegated agent, now have {len(delegate_targets)}"
                # print("number of delegated agent:", len(delegate_targets))
                # Delegate the task to other agents by publishing messages to the corresponding topics.
                for topic_type, task in delegate_targets:
                    assert (
                        len(tool_call_results) == 0
                    ), f"there shouldn't be any tool calling before delegation, number current tool call:, {len(tool_call_results)}"
                    print(
                        f"{'-'*80}\n{self.id.type}:\nDelegating to {topic_type}",
                        # f"\nyet to be published task: {len(tool_call_results)}",
                        flush=True,
                    )
                    await self.publish_message(
                        task, topic_id=TopicId(topic_type, source=self.id.key)
                    )
                    # experiment: can only delegate to one agent, and no tool can be used after delegation
                    return

            if len(tool_call_results) > 0:
                print(
                    f"{'-'*80}\n{self.id.type}:\ntool call result: {tool_call_results}",
                    flush=True,
                )
                # Make another LLM call with the results.
                message.context.extend(
                    [
                        AssistantMessage(
                            content=llm_result.content, source=self.id.type
                        ),
                        FunctionExecutionResultMessage(content=tool_call_results),
                    ]
                )
                llm_result = await self._model_client.create(
                    messages=[self._system_message] + message.context,
                    tools=self._tool_schema + self._delegate_tool_schema,
                    cancellation_token=ctx.cancellation_token,
                )
                print(
                    f"{'-'*80}\n{self.id.type}: show tool call result: \n{llm_result.content}",
                    flush=True,
                )
            else:
                # The task has been delegated, so we are done.
                return

        # The task has been completed, publish the final result.)
        assert isinstance(llm_result.content, str)
        message.context.append(
            AssistantMessage(content=llm_result.content, source=self.id.type)
        )
        await self.publish_message(
            AgentResponse(
                context=message.context, reply_to_topic_type=self._agent_topic_type
            ),
            topic_id=TopicId(self._user_topic_type, source=self.id.key),
        )


async def register_triage_agent(runtime, autogen_openai_client):
    triage_agent_prompt = """
    You are an intelligent triage assistant for a vaccination enquiry and booking system. Your goal is to direct them to the appropriate service.

    Start by introducing yourself briefly. Be polite, concise, and proactive.
    - Do not take the job of other agents, you should immediately pass the job to respective agents once the user request is clear. For example, don't ask for user's preferred date or his/her details, just pass to appointment agent once the query is relevant to booking.
    - Do not ask the user to wait or hold on. Instead, either perform the task, ask a specific question to the user, or pass control to the appropriate agent.
    - Remember, you should delegate only one agent to take up the next task, the agent will pass to subsequent agent based on its decision, and possibly come back to you.


    If the user say hi, tell them what you can provide, and ask them how you can help them today.
    If the request is unclear, politely ask for more details before routing them.
    """

    triage_agent_type = await AIAgent.register(
        runtime,
        type=triage_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: AIAgent(
            description="A triage agent.",  # The agent's role description, which indicates that it is a customer service bot for triaging issues.
            system_message=SystemMessage(content=triage_agent_prompt),
            model_client=autogen_openai_client,
            tools=[],
            delegate_tools=[  # delegate tools to transfer tasks to other agents
                transfer_to_vaccine_records_agent_tool,
                transfer_to_recommender_agent_tool,
                transfer_to_appointment_agent_tool,
            ],
            agent_topic_type=triage_agent_topic_type,  # defines the context of the agent
            user_topic_type=user_topic_type,
        ),
    )

    # Add subscriptions for the triage agent: it will receive messages published to its own topic only.
    # subscribes the triage agent to its topic (triage_agent_topic_type).
    # This ensures that the agent will receive messages that are published to this specific topic.
    # The subscription enables the triage agent to handle and respond to incoming messages directed at it.
    await runtime.add_subscription(
        TypeSubscription(
            topic_type=triage_agent_topic_type, agent_type=triage_agent_type.type
        )
    )


async def register_vaccine_records_agent(runtime, autogen_openai_client):
    vaccine_records_agent_type = await AIAgent.register(
        runtime,
        type=vaccine_records_topic_type,  # Using the topic type as the agent type.  listens for messages under the SalesAgent topic.
        factory=lambda: AIAgent(
            description="An agent responsible for retrieving user vaccination history.",
            system_message=SystemMessage(
                content="You are responsible for fetching a user's vaccination records."
                "Given NRIC, retrieve their vaccination history."
                "If no records are found, inform the requesting agent."
            ),
            model_client=autogen_openai_client,
            tools=[
                get_vaccination_history_tool
            ],  # agent can execute orders when the user agrees to buy.
            delegate_tools=[
                transfer_back_to_triage_tool,
                transfer_to_recommender_agent_tool,
            ],  # If necessary, the agent can transfer the user back to the Triage Agent.
            agent_topic_type=vaccine_records_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the sales agent: it will receive messages published to its own topic only.
    # Sales Agent subscribes to the SalesAgent topic, meaning it will only process messages published to that topic.
    await runtime.add_subscription(
        TypeSubscription(
            topic_type=vaccine_records_topic_type,
            agent_type=vaccine_records_agent_type.type,
        )
    )


async def register_vaccine_recommender_agent(runtime, autogen_openai_client):
    vaccine_recommender_agent_type = await AIAgent.register(
        runtime,
        type=vaccine_recommendation_topic_type,  # Using the topic type as the agent type.  listens for messages under the SalesAgent topic.
        factory=lambda: AIAgent(
            description="An agent responsible for recommending vaccines based on user vaccination history, age, and gender.",
            system_message=SystemMessage(
                content="You are responsible for providing personalized vaccine recommendations."
                "Use get_vaccine_recommendations_tool to get vaccinations suitable for the user based on its profile."
                "Use get_vaccination_history_tool to check the vaccination history of the user. The return from get_vaccination_history_tool are "
                "Exclude vaccines the user has already received. Provide a brief purpose for each recommended vaccine."
                "The backend will handle the profile retrieval, you can just safely call the function without asking any information from the user."
            ),
            model_client=autogen_openai_client,
            tools=[
                get_vaccination_history_tool,
                get_vaccine_recommendations_tool,
                # recommend_vaccines_tool,
            ],  # agent can execute orders when the user agrees to buy.
            delegate_tools=[
                transfer_back_to_triage_tool,
                transfer_to_appointment_agent_tool,
            ],  # If necessary, the agent can transfer the user back to the Triage Agent.
            agent_topic_type=vaccine_recommendation_topic_type,
            user_topic_type=user_topic_type,
        ),
    )

    # Add subscriptions for the sales agent: it will receive messages published to its own topic only.
    # Sales Agent subscribes to the SalesAgent topic, meaning it will only process messages published to that topic.
    await runtime.add_subscription(
        TypeSubscription(
            topic_type=vaccine_recommendation_topic_type,
            agent_type=vaccine_recommender_agent_type.type,
        )
    )


async def register_appointment_agent(runtime, autogen_openai_client):
    appointment_agent_type = await AIAgent.register(
        runtime,
        type=appointment_topic_type,  # Using the topic type as the agent type.  listens for messages under the SalesAgent topic.
        factory=lambda: AIAgent(
            description="An agent responsible for managing vaccination appointments, including checking availability and booking or modifying appointments.",
            system_message=SystemMessage(
                content="You are responsible for managing vaccination appointments."
                "You help users check available slots, book new appointments, reschedule existing ones, or cancel appointments."
                "If any information is missing, request clarification from the user before proceeding."
                "Do not pass the task to another agent until your task is completed or you require another agent to take over."
                "Do not ask the user to wait or hold on. Instead, either perform the task, ask a specific question to the user, or pass control to the appropriate agent."
                """
                Follow the flow interactively guide the user to book a slot.
                If some of the information is present, you can skip the steps of asking user for it.
                You already have access to the user’s profile including their enrolled_clinic in their details (not the nearest clinic), so you don’t need to retrieve user details again.

                Here's how you operate:

                #### 🏥 Clinic Enrollment Confirmation
                - Check {user_enrolled_clinic}. If there is no enrolled clinic, ask user if he/she wans to check on nearby polyclinic or GP.
                - If there is a enrolled clinic, and {user_enrolled_clinic.type} is gp, jump to the below flow about gp and ask:
                    > *You're enrolled at **{user_enrolled_clinic_name}**. I am sorry that I can only book for vaccination appointment at polyclinic, you can book your vaccination on https://book.health.gov.sg, let me know if you want to book appointment at polyclinic*
                - If there is a enrolled clinic, and {user_enrolled_clinic.type} is polyclinic. continue with asking:
                    > You're enrolled at **{user_enrolled_clinic_name}** (retrieve this from user's detail in previous message). Would you like me to check for available vaccination slots there?

                - If **Yes**: proceed to vaccine selection if the user hasn't specify which vaccine to take.
                - If **No**:
                - Ask:
                    > *Would you like me to look at other Polyclinics for available slots instead?*, with slight modification on what user has mentioned
                - If **Yes**: call `get_nearest_polyclinic_tool` with 'polyclinic' as the clinic_type parameter to recommend nearby polyclinic
                - If **No**:
                - Ask:
                    > *Would you like to check up on nearby general practitioner (GP)?
                - If **No**:
                    > *Alright, I'm sorry I couldn’t help this time. Let me know if there’s anything else I can assist with.*
                - If **Yes**: call `get_nearest_polyclinic_tool` with 'gp' as the clinic_type parameter to recommend nearby GP
                    > *This is the nearby GP: <show the list>. I am sorry that I can only book for vaccination appointment at polyclinic, you can book your vaccination on https://book.health.gov.sg*

                ---

                #### 💉 Vaccine Selection
                - Available vaccination type list: ['Influenza (INF)', 'Pneumococcal Conjugate (PCV13)', 'Human Papillomavirus (HPV)', 'Tetanus, Diphtheria, Pertussis Tdap)', 'Hepatitis B (HepB)', 'Measles, Mumps, Rubella (MMR)', 'Varicella (VAR)'] )
                - Show the vaccination history of the user by calling `get_vaccination_history_tool`
                \t- {vaccination_name_1}, status: {status_1}
                \t- {vaccination_name_2}, status: {status_2}
                - If user mentioned a vaccine type or a related disease, show them the available list and tell them which one matches or none of them matches.
                - If none of the vaccine matches, and user don't want take any from the available list, tell them sorry you can't help.
                - If the user didn't specify a vaccine type or a related disease to take, ask:
                > *Which vaccine are you interested in?* with all the Available vaccination type list shown
                - When you try to check for available slot, convert the selected vaccine name to the exact corresponding name in the Available vaccination type list, proceed to fetch available slots using the converted name
                ---

                #### 📅 Desired Date and Time
                - Ask the user for their preferred time interval. Please provide the start and end dates for filtering.
                - If the user said "roughly next week", "around next Sunday", you will do the gauging yourself and come out with the `start_datetime` and `end_datetime`
                - Convert both preferred times into ISO 8601 format "YYYY-MM-DDTHH:MM:SS".

                ---

                #### 📅 Fetch Available Slots
                - Use get_available_booking_slots_tool
                - Parameters:
                    - `vaccine_name` (required, You have to convert the name in user's reply to the verbatim name from the available vaccination type list.)
                    - `polyclinic_name = enrolled_clinic.name`
                    - `start_datetime` (ISO 8601 format "YYYY-MM-DDTHH:MM:SS")
                    - `end_datetime` (ISO 8601 format "YYYY-MM-DDTHH:MM:SS")

                ---

                #### 🗓️ Display Slot Options
                - From the JSON response, display:
                > *Here are the available slots for **{vaccine_name}** at **{enrolled_clinic.name}**.*
                > *Please select a slot you'd like to book:*
                    - Slot 1 (Date, Time, clinic) (booking id: ...)
                    - Slot 2 (Date, Time, clinic) (booking id: ...)
                    - Slot 3 (Date, Time, clinic) (booking id: ...)
                    - ... (show all retrieved slots, up to ten slots)

                ---

                #### ✅ Confirm Booking
                - Once a slot is selected, confirm details:
                > *Great! Here's your booking summary:*
                    • Polyclinic: **{enrolled_clinic.name}**
                    • Vaccine: **{vaccine_name}**
                    • Date: **{datetime.date}**
                    • Time: **{datetime.time}**
                    • Time: **{booking_slot_id}**
                    > *Would you like to proceed with this booking?*

                ---

                #### 📥 Finalize Appointment
                - If **Yes**:
                - Use tool:
                    ```
                    schedule_vaccination_slot_tool()
                    ```
                    - with `booking_slot_id`
                - Respond:
                    ✅ *Your appointment has been successfully scheduled!*

                - If **No**: handle fallback logic as needed.

                ---

                """
            ),
            model_client=autogen_openai_client,
            tools=[
                get_nearest_polyclinic_tool,
                get_vaccination_history_tool,
                get_available_booking_slots_tool,
                cancel_booking_tool,
                schedule_vaccination_slot_tool,
            ],  # agent can execute orders when the user agrees to buy.
            delegate_tools=[
                transfer_back_to_triage_tool,
                transfer_to_recommender_agent_tool,
            ],  # If necessary, the agent can transfer the user back to the Triage Agent.
            agent_topic_type=appointment_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the sales agent: it will receive messages published to its own topic only.
    # Sales Agent subscribes to the SalesAgent topic, meaning it will only process messages published to that topic.
    await runtime.add_subscription(
        TypeSubscription(
            topic_type=appointment_topic_type, agent_type=appointment_agent_type.type
        )
    )
