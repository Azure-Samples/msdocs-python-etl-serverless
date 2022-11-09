import logging
import os

from azure.storage.filedatalake import DataLakeServiceClient


# RBAC role - Storage Blob Data Owner
def upload_to_data_lake(azure_credential, file_name, data_str):

    account_name = os.environ.get("DATALAKE_GEN_2_RESOURCE_NAME")
    container_name = os.environ.get("DATALAKE_GEN_2_CONTAINER_NAME")
    directory_name = os.environ.get("DATALAKE_GEN_2_DIRECTORY_NAME")

    unique_file_path = f"{file_name}"
    logging.info("unique_file_path: %s", unique_file_path)

    # Azure SDK client
    service_client = DataLakeServiceClient(
        account_url="{}://{}.dfs.core.windows.net".format("https", account_name),
        credential=azure_credential,
    )

    file_system_client = service_client.get_file_system_client(file_system=container_name)
    directory_client = file_system_client.get_directory_client(directory_name)
    file_client = directory_client.get_file_client(unique_file_path)
    file_client.upload_data(data_str, overwrite=True)
    logging.info("Successfully uploaded data to data lake at %s.", unique_file_path)

    return unique_file_path
