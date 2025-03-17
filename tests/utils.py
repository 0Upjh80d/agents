from typing import Awaitable, Callable, TypedDict

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI, OpenAI
from pydantic import BaseModel


class AuthArgs(TypedDict, total=False):
    """Specify a Class to hold the authentication parameters."""

    api_key: str
    azure_ad_token_provider: Callable[[], str | Awaitable[str]]


class ModelConfig(BaseModel):
    api: str
    format: str
    name: str
    version: int | str


class SkuConfig(BaseModel):
    capacity: int
    name: str


class DeploymentConfig(BaseModel):
    apiVersion: str
    endpointUri: str
    model: ModelConfig
    name: str
    platform: str
    sku: SkuConfig
    apiKey: str | None = None


class Deployments(BaseModel):
    configs: list[DeploymentConfig]


def create_client(
    endpoint: str,
    deployment: str,
    api_version: str,
    api_key: str | None = None,
) -> OpenAI | AzureOpenAI:
    # Keyless authentication via Azure AD
    azure_credential = DefaultAzureCredential(
        exclude_shared_token_cache_credential=True
    )
    # If API Key is not set, returns None and Azure AD will be used
    aoai_credential: TokenCredential | AzureKeyCredential = (
        azure_credential if api_key is None else AzureKeyCredential(api_key)
    )

    # Check if API Key was used or Azure AD
    auth_args = AuthArgs()

    # If API Key was used, assign it to AuthArgs
    if isinstance(aoai_credential, AzureKeyCredential):
        print("Using API Key.")
        auth_args["api_key"] = aoai_credential
    elif isinstance(aoai_credential, TokenCredential):
        print("Using Azure AD.")
        auth_args["azure_ad_token_provider"] = get_bearer_token_provider(
            aoai_credential, "https://cognitiveservices.azure.com/.default"
        )
    else:
        raise TypeError("Invalid credential type")

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        azure_deployment=deployment,
        api_version=api_version,
        **auth_args,
    )

    return client
