import json
import os

from dotenv import load_dotenv

from tests.utils import DeploymentConfig, Deployments, create_client

load_dotenv(".azure/agents/.env")

# Get all deployments
DEPLOYMENTS = os.getenv("DEPLOYMENTS")

configs = [DeploymentConfig(**cfg) for cfg in json.loads(DEPLOYMENTS)]
deployments = Deployments(configs=configs)


def test_chat():
    for deployment in deployments.configs:
        client = create_client(
            endpoint=deployment.endpointUri,
            deployment=deployment.name,
            api_version=deployment.apiVersion,
        )

        if deployment.model.api == "chat":
            response = client.chat.completions.create(
                model=deployment.model.name,
                messages=[{"role": "user", "content": "Hello!"}],
            )

            assert response is not None
            assert len(choices := response.choices) > 0
            assert (choice := choices[0]) is not None
            assert (message := choice.message) is not None
            assert message.content is not None


def test_embedding():
    for deployment in deployments.configs:
        client = create_client(
            endpoint=deployment.endpointUri,
            deployment=deployment.name,
            api_version=deployment.apiVersion,
        )

        if deployment.model.api == "embeddings":
            response = client.embeddings.create(
                model=deployment.model.name, input=["Hello"]
            )

            assert response is not None
            assert len(datas := response.data) > 0
            assert datas[0] is not None
            assert (embedding := datas[0].embedding) is not None
            assert embedding is not None
            assert len(embedding) >= 512
