from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential


def get_azure_default_credential():
    return DefaultAzureCredential(additionally_allowed_tenants=["*"])


def get_azure_key_credential(key):
    return AzureKeyCredential(key)
