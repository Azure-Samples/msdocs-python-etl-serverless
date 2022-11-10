# ./shared/azure_credential.py
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential


# Get authentication with environment variables
def get_azure_default_credential():
    return DefaultAzureCredential(additionally_allowed_tenants=["*"])


# Get authentication with key
def get_azure_key_credential(key):
    return AzureKeyCredential(key)
