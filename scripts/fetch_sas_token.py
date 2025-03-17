#!/usr/bin/env python3

"""
`fetch_sas_token.py`

Reads/Updates a `.env` file with `AZURE_STORAGE_SAS_TOKEN`, checks expiry,
and fetches a new token from Azure Key Vault if needed.

Usage:
    `python fetch_sas_token.py`
    OR make it executable and run:
        `./fetch_sas_token.py`

    But first make sure to change its permissions to allow execution:
        `chmod +x fetch_sas_token.py`

The final SAS token (valid or newly fetched) is set in the `.env`.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any

from azure.core.exceptions import ResourceNotFoundError, ServiceRequestError
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets import KeyVaultSecret
from azure.keyvault.secrets.aio import SecretClient
from dotenv import load_dotenv

load_dotenv()

AZURE_KEY_VAULT = os.getenv("AZURE_KEY_VAULT")
SECRET_NAME = os.getenv("SECRET_NAME")
SAS_TOKENS = [
    {
        "env_var_name": "AZURE_STORAGE_SAS_TOKEN",
        "secret_name": SECRET_NAME,
    },
]


def save_env(env_file: str, key: str, value: str) -> None:
    """
    Writes the key=value pairs back into the .env file.
    Overwrites entire file (simple approach).
    Values are written as key="value".

    Args:
        env_file (str): The path to the .env file.
        key (str): The key to write.
        value (str): The value to write.
    """
    # Ensure the file exists even if empty
    if not os.path.exists(env_file):
        with open(env_file, "w", encoding="utf-8"):
            pass  # create empty file

    # Read all lines
    with open(env_file, encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    found_key = False

    for line in lines:
        # Strip whitespace so we can match lines robustly
        stripped = line.strip()
        # Check if this line starts with the key and an '='
        # e.g. AZURE_STORAGE_SAS_TOKEN= or AZURE_STORAGE_SAS_TOKEN="..."
        if stripped.startswith(f"{key}="):
            # Replace this line with the new key=value pair
            new_lines.append(f'{key}="{value}"')
            found_key = True
        else:
            new_lines.append(stripped)  # keep original line

    # If the key wasn't found, append a new line
    if not found_key:
        new_lines.append(f'{key}="{value}"')

    new_lines = [line + "\n" for line in new_lines]

    # Rewrite the file with updated contents
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def extract_expiry_timestamp(sas_token: str) -> int | None:
    """
    Extracts the `se=YYYY-MM-DDTHH:MM:SSZ` parameter from a SAS token,
    parses the datetime, and returns a UTC timestamp (int).
    Returns None if parsing fails.

    Example SAS token snippet:
        "...?sv=...&se=2025-01-01T00%3A00%3A00Z&sr=..."
        or
        "...&se=2025-01-01T00:00:00Z&..."

    Args:
        sas_token (str): The SAS token to parse.

    Returns:
        int | None: The parsed timestamp, or None if parsing fails.
    """
    import urllib.parse

    # We decode the token in case the date/time is URL-encoded (e.g., 2025-01-01T00%3A00%3A00Z)
    decoded = urllib.parse.unquote(sas_token)

    # Attempt a quick parse for `se=...`
    # e.g. "...&se=2025-01-01T00:00:00Z&sr=..."
    parts = decoded.split("&")
    expiry_value = None
    for p in parts:
        if p.startswith("se="):
            expiry_value = p[3:]
            break

    if not expiry_value:
        return None  # could not find se=

    # If your token has fractional seconds or offset, adjust as needed.
    try:
        # Trim any trailing 'Z' if present, for strptime.
        # We'll assume it's UTC.
        if expiry_value.endswith("Z"):
            expiry_value = expiry_value[:-1]

        dt = datetime.strptime(expiry_value, "%Y-%m-%dT%H:%M:%S")
        # Interpret as UTC
        return int(dt.timestamp())
    except ValueError:
        return None


async def fetch_sas_token(secret_name: str) -> Any | str | None:
    """
    Fetches a SAS token from Azure Key Vault.

    Args:
        secret_name (str): The name of the secret for the SAS token.

    Returns:
        Any | str | None: The SAS token, or None if fetching fails.
    """
    async with DefaultAzureCredential(
        exclude_shared_token_cache_credential=True
    ) as credential:
        async with SecretClient(
            vault_url=f"https://{AZURE_KEY_VAULT}.vault.azure.net/",
            credential=credential,
        ) as keyvault_client:
            secret_key_obj: KeyVaultSecret = await keyvault_client.get_secret(
                secret_name
            )  # Gets latest version
            secret_key = secret_key_obj.value
            return secret_key


async def main() -> None:
    try:
        for sas_token in SAS_TOKENS:
            env_var_name = sas_token["env_var_name"]
            sas_token_value = os.getenv(env_var_name)
            if sas_token_value is not None:
                expiry_ts = extract_expiry_timestamp(sas_token_value)
                if expiry_ts is not None:
                    now_ts = int(datetime.now().timestamp())
                    if expiry_ts > now_ts:
                        # Valid SAS token; output and exit
                        print(
                            f"👍 No update required. {env_var_name} is set and not expired."
                        )
                        continue
                    else:
                        print(
                            f"⌛ {env_var_name} in .env is expired. Fetching a new SAS token."
                        )
                else:
                    print(
                        f"👎 {env_var_name} in .env is malformed or missing 'se=' parameter hence expiry not verified. Fetching a new SAS token."
                    )
            else:
                print(f"🤷‍♂️ No {env_var_name} in .env. Fetching from Azure Key Vault.")
            try:
                secret_name = sas_token["secret_name"]
                secret_key = await fetch_sas_token(secret_name)
                save_env(".env", env_var_name, secret_key)
                print(f"✅ Successfully set {env_var_name}.")

            except ResourceNotFoundError:
                print(
                    f"❌ Secret not found. Please check that {secret_name} is named correctly and present in {AZURE_KEY_VAULT}."
                )
            except ServiceRequestError:
                print(
                    f"❌ Request to Azure Key Vault unsucessful. Please check that the {AZURE_KEY_VAULT} has been named correctly."
                )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)  # Exit with error


if __name__ == "__main__":
    asyncio.run(main())
