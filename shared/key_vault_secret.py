import logging

from azure.keyvault.secrets import SecretClient


def get_key_vault_secret(azure_credential, key_vault_name, secret_name):

    # TODO: Does this need to have hyphens stripped?
    key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
    logging.info("key_vault_uri=%s", key_vault_uri)

    client = SecretClient(vault_url=key_vault_uri, credential=azure_credential)
    logging.info("created client")

    key_vault_secret_response = client.get_secret(secret_name)
    logging.info("got secret")
    logging.info("secret= %s, value= %s", secret_name, key_vault_secret_response.value)

    return key_vault_secret_response.value
