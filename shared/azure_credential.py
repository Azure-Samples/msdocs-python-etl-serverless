from azure.identity import DefaultAzureCredential


def get_azure_credential():
    return DefaultAzureCredential(additionally_allowed_tenants=["*"])
