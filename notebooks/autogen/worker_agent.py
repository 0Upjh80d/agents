import json
import pprint
from typing import List, Tuple

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
from autogen_core.tools import FunctionTool, Tool

# Message types
from message_type import AgentResponse, UserTask

pp = pprint.PrettyPrinter(indent=4)


def fetch_vaccination_history():
    return "Temp: You have received the following vaccinations: Influenza, Hepatitis A, Hepatitis B, Tetanus, and HPV, but not Covid-19"


def fetch_user_profile():
    return "Temp: Your age is 20, gender male"


def recommend_vaccines():
    return "Temp: I recommend that you get the COVID-19 booster shot."


def check_available_slots():
    return "Temp: There is no available slots at the moment at Clementi Polyclinic. \n\
        But there is available slots for Covid-19 vaccination at Bukit Batok Polyclinic on 10 March 2025, 3:00pm and 4:00pm."


def book_appointment():
    return "Temp: Your appointment has been booked."


fetch_vaccination_history_tool = FunctionTool(
    fetch_vaccination_history,
    description="Use to retrieve user's vaccination history records based on user id.",
)
fetch_user_profile_tool = FunctionTool(
    fetch_user_profile,
    description="Use to retrieve user profile information such as gender and date of birth based on user id.",
)
recommend_vaccines_tool = FunctionTool(
    recommend_vaccines,
    description="Provide personalised vaccine recommendations based on user's vaccination history, age and gender.",
)
check_slots_tool = FunctionTool(
    check_available_slots,
    description="Check for available vaccination appointment slots based on vaccine name, polyclinic name and date.",
)
book_appointment_tool = FunctionTool(
    book_appointment,
    description="User to book, cancel or reschedule a vaccination appointment.",
)


def transfer_to_vaccine_records_agent() -> str:
    return vaccine_records_topic_type


def transfer_to_recommender_agent() -> str:
    return vaccine_recommendation_topic_type


def transfer_to_appointment_agent() -> str:
    return appointment_topic_type


def transfer_back_to_triage() -> str:
    return triage_agent_topic_type


def transfer_to_general_query_agent() -> str:
    return


transfer_to_general_query_agent_tool = FunctionTool(
    transfer_to_general_query_agent,
    description="Use for general queries.",
)

transfer_to_vaccine_records_agent_tool = FunctionTool(
    transfer_to_vaccine_records_agent,
    description="Use for retrieval of vaccination records history.",
)
transfer_to_recommender_agent_tool = FunctionTool(
    transfer_to_recommender_agent,
    description="Use for recommendation of vaccinations for user based on user's vaccination history, age and gender.",
)
transfer_to_appointment_agent_tool = FunctionTool(
    transfer_to_appointment_agent,
    description="Use for vaccination-related appointments enquiry, booking, cancellation and rescheduling.",
)
transfer_back_to_triage_tool = FunctionTool(
    transfer_back_to_triage,
    description="Call this if the user brings up a topic outside of your purview.",
)

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

    @message_handler
    async def handle_task(self, message: UserTask, ctx: MessageContext) -> None:
        # Send the task to the LLM.
        llm_result = await self._model_client.create(
            messages=[self._system_message] + message.context,
            tools=self._tool_schema + self._delegate_tool_schema,
            cancellation_token=ctx.cancellation_token,
        )
        print(f"{'-'*80}\n{self.id.type}:", flush=True)
        print(
            f"number of task: {len(llm_result.content) if isinstance(llm_result.content, list) else "NA"}",
            flush=True,
        )
        if isinstance(llm_result.content, list):
            print("llm_reselt.content:")
            for fun in llm_result.content:
                print(fun, flush=True)
        else:
            print("llm_reselt.content:", llm_result.content, flush=True)

        # Process the LLM result.
        while isinstance(llm_result.content, list) and all(
            isinstance(m, FunctionCall) for m in llm_result.content
        ):
            tool_call_results: List[FunctionExecutionResult] = []
            delegate_targets: List[Tuple[str, UserTask]] = []
            print("x" * 40, "START A NEW ITERATION IN WHILE ", "x" * 40, flush=True)
            # Process each function call.
            for call in llm_result.content:
                print("o" * 40, "each call in llm_result", "o" * 40, flush=True)
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
                                    content=f"Transferred to {topic_type}. Adopt persona immediately.",
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
                # Delegate the task to other agents by publishing messages to the corresponding topics.
                for topic_type, task in delegate_targets:
                    print(
                        f"{'-'*80}\n{self.id.type}:\nDelegating to {topic_type}",
                        f"\n yet to be published task: {len(tool_call_results)}",
                        flush=True,
                    )
                    await self.publish_message(
                        task, topic_id=TopicId(topic_type, source=self.id.key)
                    )

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
    You are an intelligent triage assistant for a vaccination enquiry and booking system. Your goal is to efficiently guide users by gathering key details and directing them to the appropriate service.
    Start by introducing yourself briefly. Ask clear, natural, and relevant questions to collect necessary information without overwhelming the user. Be polite, concise, and proactive.
    Gather information to direct the customer to the right agent.
    If the user say hi, tell them what you can provide, and ask them how you can help them today.
    If the user requests a vaccination appointment but does not specify a preferred date or location or vaccine name, ask them to provide the missing details before proceeding.
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
    await runtime.add_subscription(
        TypeSubscription(
            topic_type=appointment_topic_type, agent_type=triage_agent_type.type
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
                fetch_vaccination_history_tool
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
                "Given a user's vaccination history, age, and gender, suggest appropriate vaccines."
                "Exclude vaccines the user has already received. Provide a brief purpose for each recommended vaccine."
            ),
            model_client=autogen_openai_client,
            tools=[
                fetch_vaccination_history_tool,
                fetch_user_profile_tool,
                recommend_vaccines_tool,
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
                "Ensure all necessary information is provided, such as vaccine name, polyclinic location, and preferred date."
                "If any information is missing, request clarification before proceeding."
            ),
            model_client=autogen_openai_client,
            tools=[
                book_appointment_tool,
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
