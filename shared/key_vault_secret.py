import logging
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


def get_key_vault_secret(key_vault_name, secret_name):

    azure_credential = DefaultAzureCredential(additionally_allowed_tenants=["*"])
    key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
    logging.info(f"key_vault_uri={key_vault_uri}")

    client = SecretClient(vault_url=key_vault_uri, credential=azure_credential)
    logging.info(f"created client")

    key_vault_secret_response = client.get_secret(secret_name)
    logging.info("got secret")
    logging.info(f"secret= {secret_name}, value= {key_vault_secret_response.value}")

    return key_vault_secret_response.value
