import os

from dotenv import load_dotenv


def get_gemini_api_key() -> str:
    """Load the Gemini API key from Azure Key Vault or local environment."""
    load_dotenv()

    key_vault_url = os.getenv("KEY_VAULT_URL")

    if key_vault_url:
        # Import Azure packages only when Key Vault is configured.
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        credential = DefaultAzureCredential()
        client = SecretClient(
            vault_url=key_vault_url,
            credential=credential,
        )

        secret = client.get_secret("GEMINI-API-KEY")
        api_key = secret.value
    else:
        # Local development: read the key from the ignored .env file.
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Gemini API key is not configured. Set GEMINI_API_KEY "
            "locally or configure GEMINI-API-KEY in Azure Key Vault."
        )

    return api_key
