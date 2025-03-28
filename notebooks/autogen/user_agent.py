# testing openai connection
from autogen_core import (
    MessageContext,
    RoutedAgent,
    TopicId,
    TypeSubscription,
    message_handler,
)
from autogen_core.models import (
    UserMessage,
)
from message_type import AgentResponse, UserLogin, UserTask

# define the topic types each of the agents will subscribe to
vaccine_records_topic_type = "VaccineRecordsAgent"
vaccine_recommendation_topic_type = "VaccineRecommenderAgent"
appointment_topic_type = "AppointmentAgent"
triage_agent_topic_type = "TriageAgent"
user_topic_type = "User"  # HealthHub AI


class UserAgent(RoutedAgent):
    def __init__(
        self, description: str, user_topic_type: str, agent_topic_type: str
    ) -> None:
        super().__init__(description)
        self._user_topic_type = user_topic_type
        self._agent_topic_type = agent_topic_type

    @message_handler
    async def handle_user_login(self, message: UserLogin, ctx: MessageContext) -> None:
        print(f"{'-'*80}\nUser login, session ID: {self.id.key}.", flush=True)
        # Get the user's initial input after login.
        user_input = input("User: ")
        print(f"{'-'*80}\n{self.id.type}:\n{user_input}")
        await self.publish_message(
            UserTask(context=[UserMessage(content=user_input, source="User")]),
            topic_id=TopicId(self._agent_topic_type, source=self.id.key),
        )

    # User Login: First Interaction
    # Triggered when a user logs in.
    # Asks for user input and sends it to the Triage Agent.
    # The Triage Agent then determines which agent should handle the request.

    @message_handler
    async def handle_task_result(
        self, message: AgentResponse, ctx: MessageContext
    ) -> None:
        # Get the user's input after receiving a response from an agent.
        user_input = input("User (type 'exit' to close the session): ")
        print(f"{'-'*80}\n{self.id.type}:\n{user_input}", flush=True)
        if user_input.strip().lower() == "exit":
            print(f"{'-'*80}\nUser session ended, session ID: {self.id.key}.")
            return
        message.context.append(UserMessage(content=user_input, source="User"))
        await self.publish_message(
            UserTask(context=message.context),
            topic_id=TopicId(message.reply_to_topic_type, source=self.id.key),
        )

    # Handling Agent Responses: Continuing the Conversation
    # Waits for an agent's response.
    # Prompts the user for their next input.
    # If the user types "exit", the session ends.
    # Otherwise, the conversation continues by forwarding the updated context.

    def set_token(self, token: str) -> None:
        self._token = token

    def get_token(self) -> str:
        return self._token


async def register_user_agent(runtime):
    user_agent_type = await UserAgent.register(
        runtime,
        type=user_topic_type,  # agent listens to messages under the "User" topic.
        factory=lambda: UserAgent(
            description="A user agent.",
            user_topic_type=user_topic_type,
            agent_topic_type=triage_agent_topic_type,  # Start with the triage agent.
        ),
    )
    # Add subscriptions for the user agent: it will receive messages published to its own topic only.
    # Ensures the User Agent only processes messages under the "User" topic.
    await runtime.add_subscription(
        TypeSubscription(topic_type=user_topic_type, agent_type=user_agent_type.type)
    )
