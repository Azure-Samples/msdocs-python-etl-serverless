# ./shared/key_vault_secret.py
import logging

from azure.keyvault.secrets import SecretClient


# Get a secret from Azure Key Vault
def get_key_vault_secret(azure_credential, key_vault_name, secret_name):

    # TODO: Does this need to have hyphens stripped?
    key_vault_uri = f"https://{key_vault_name}.vault.azure.net"

    # Get the client
    client = SecretClient(vault_url=key_vault_uri, credential=azure_credential)

    # Get the secret
    key_vault_secret_response = client.get_secret(secret_name)

    return key_vault_secret_response.value
