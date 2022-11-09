import os, uuid, sys, logging
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core._match_conditions import MatchConditions
from azure.storage.filedatalake._models import ContentSettings

# RBAC role - Storage Blob Data Owner


def upload_to_data_lake(file_name, data_str):

    account_name = os.environ.get("DATALAKE_GEN_2_RESOURCE_NAME")
    container_name = os.environ.get("DATALAKE_GEN_2_CONTAINER_NAME")
    directory_name = os.environ.get("DATALAKE_GEN_2_DIRECTORY_NAME")

    unique_file_path = f"{file_name}"
    logging.info(f"unique_file_path: {unique_file_path}")

    azure_credential = DefaultAzureCredential(additionally_allowed_tenants=["*"])

    # Azure SDK client
    service_client = DataLakeServiceClient(
        account_url="{}://{}.dfs.core.windows.net".format("https", account_name),
        credential=azure_credential,
    )

    file_system_client = service_client.get_file_system_client(
        file_system=container_name
    )
    directory_client = file_system_client.get_directory_client(directory_name)
    file_client = directory_client.get_file_client(unique_file_path)
    file_client.upload_data(data_str, overwrite=True)
    logging.info(f"Successfully uploaded data to data lake at {unique_file_path}.")

    return unique_file_path
